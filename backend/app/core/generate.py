"""LLM generation helpers using OpenRouter.

Provides async and sync wrappers to generate answers using OpenRouter APIs
and helper functions that call the remote LLM with retries and fallbacks.
"""

import os
import asyncio
import concurrent.futures
import logging
from typing import Dict, Tuple, Optional
import httpx
from .prompts import build_qa_prompt
from .config import settings

logger = logging.getLogger(__name__)


async def generate_answer(
    question: str, context: str, intake_data: Dict = None, prompt: str = None
) -> str:
    """Generate answer using OpenRouter API with intake context or custom prompt."""
    if prompt is None:
        prompt = build_qa_prompt(question, context, intake_data)

    return await _call_openrouter_api(prompt)


async def _call_openrouter_api(prompt: str) -> str:
    """Call OpenRouter API for LLM generation using free models."""
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        logger.error("OPENROUTER_API_KEY not found in settings")
        return (
            "I'm sorry, I'm currently unable to process your request. "
            "Please contact support."
        )

    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("YOUR_SITE_URL", "http://localhost:3000"),
        "X-Title": "BoBeutician - AI Skincare Consultant",
    }

    # List of free models to try in order of preference
    free_models = [
        "meta-llama/llama-3.3-70b-instruct:free",
    ]

    model = settings.LLM_MODEL

    # If the set model isn't in our free list, use the first free model
    if model not in free_models:
        model = free_models[0]

    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a knowledgeable skincare consultant providing helpful, "
                "safe advice. Be specific about products mentioned and always recommend patch "
                "testing. Keep responses under 800 words.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 800,  # Reduced to work better with free models
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
    }

    final_answer = None
    for attempt, model_to_try in enumerate(free_models):
        if attempt > 0:
            logger.info("Trying alternative free model: %s", model_to_try)

        answer, fallback = await _attempt_model_call(
            url, headers, data, model_to_try, attempt == len(free_models) - 1
        )
        if answer:
            final_answer = answer
            break
        if fallback:
            final_answer = fallback
            break

    if final_answer:
        return final_answer

    return "I'm currently unable to process your request. Please try again later."


async def _attempt_model_call(
    url: str,
    headers: dict,
    data: dict,
    model_to_try: str,
    last_attempt: bool,
) -> Tuple[Optional[str], Optional[str]]:
    """Attempt a single model call; returns (answer, fallback_message).

    Uses a single return at the end to keep the function's return count low.
    """
    final_answer: Optional[str] = None
    final_fallback: Optional[str] = None

    local_data = dict(data)
    local_data["model"] = model_to_try

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=local_data, headers=headers)
            response.raise_for_status()

            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                final_answer = result["choices"][0]["message"]["content"].strip()
                logger.info(
                    "Successfully generated a %d-character response with %s",
                    len(final_answer),
                    model_to_try,
                )
            else:
                logger.warning(
                    "Unexpected API response format with %s: %s",
                    model_to_try,
                    result,
                )
                if last_attempt:
                    final_fallback = (
                        "I apologize, but I'm having trouble generating a response right now. "
                        "Please try again."
                    )

    except (httpx.TimeoutException, httpx.RequestError) as exc:
        # Network-related errors share similar handling: warn and provide a
        # last-attempt fallback message.
        logger.warning("Network/request error with model %s: %s", model_to_try, exc)
        if last_attempt:
            final_fallback = (
                "I'm having technical difficulties with network communication. "
                "Please try again or contact support."
            )

    except httpx.HTTPStatusError as e:
        logger.warning("Model %s HTTP error: %s", model_to_try, e.response.status_code)
        code = e.response.status_code
        if code == 401:
            final_fallback = (
                "I'm experiencing authentication issues. Please contact support."
            )
        elif code == 429 and last_attempt:
            final_fallback = (
                "All free models are currently experiencing high demand. "
                "Please try again in a few minutes."
            )
        elif last_attempt:
            final_fallback = (
                "I'm having technical difficulties. "
                "Please try again or contact support."
            )

    except ValueError as e:
        logger.warning("Invalid response from model %s: %s", model_to_try, e)
        if last_attempt:
            final_fallback = "I encountered an unexpected response format." \
            "Please try again or contact support."

    return final_answer, final_fallback


def generate_answer_sync(question: str, context: str, prompt: str = None) -> str:
    """Synchronous wrapper for generate_answer."""

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If event loop is already running, create a task
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, generate_answer(question, context, prompt)
                )
                return future.result()
        else:
            return loop.run_until_complete(generate_answer(question, context, prompt))
    except RuntimeError:
        # If no event loop is running, create a new one
        return asyncio.run(generate_answer(question, context, prompt))
