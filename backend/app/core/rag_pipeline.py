"""Orchestration pipeline that retrieves, composes, and generates responses.

This module coordinates SQL-backed retrieval, optional reranking, context
composition, and LLM generation to produce personalized skincare
recommendations consumed by the API endpoints.
"""

from typing import List, Dict
import logging
import asyncio

from .generate import generate_answer
from .compose import compose_context
from .hybrid_retrieve import sql_retrieve
from .prompts import build_qa_prompt

logger = logging.getLogger(__name__)


async def run_pipeline(
    question: str,
    db_session=None,
    intake_data: Dict = None,
    concern: str | None = None,
    k: int = 8,
) -> dict:
    """Run SQL-backed retrieval pipeline with intake form integration.

    Args:
        question: User's natural language question
        db_session: Database session
        intake_data: User's intake form responses
        concern: Additional concern parameter
        k: Number of results to retrieve

    Returns:
        Complete skincare recommendation with personalized context
    """
    try:
        logger.info("Starting retrieval pipeline for query: %s...", question[:50])

        # SQL-backed retrieval with intake data
        results = sql_retrieve(
            db_session=db_session,
            query=question,
            intake_data=intake_data,
            concern=concern,
            k=k,
        )

        if not results:
            logger.warning("No results retrieved for query")
            return _create_fallback_response(question, intake_data)

        logger.info("Retrieved %d results", len(results))

        # No reranker: use retrieval order directly
        ordered_results = results

        # Context composition with intake data
        composed = compose_context(
            results=ordered_results,
            token_budget=500,  # Increased budget for richer context
            intake_data=intake_data,
        )

        try:
            prompt = build_qa_prompt(question, composed["summary"], intake_data)
            answer = await generate_answer(
                question,
                composed["summary"],
                intake_data=intake_data,
                prompt=prompt,
            )
            logger.info("Successfully generated answer using LLM")
        except asyncio.CancelledError as e:
            # Log and propagate cancellation to allow graceful shutdowns
            logger.info("Answer generation cancelled: %s", e)
            raise
        except (TimeoutError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error("Answer generation failed: %s", e)
            # Create manual response instead of raising
            answer = _create_manual_response(composed, intake_data)

        # Create comprehensive response
        response = {
            "answer": answer,
            "context_summary": composed["summary"],
            "user_profile": composed.get("user_profile", ""),
            "citations": composed["citations"],
            "used_results": composed["used_results"],
            "recommendation_confidence": _calculate_confidence(results, intake_data),
            "routine_suggestion": _extract_routine_from_context(composed["summary"]),
        }

        logger.info("Retrieval pipeline completed successfully")
        return response

    except (RuntimeError, ValueError, ConnectionError, OSError) as e:
        logger.error("Retrieval pipeline failed: %s", e, exc_info=True)
        return _create_error_response(question, intake_data, str(e))


def _create_fallback_response(question: str, intake_data: Dict = None) -> dict:
    """Create a helpful fallback response when no products are found."""
    profile_text = ""
    if intake_data:
        skin_type = intake_data.get("skin_type", "")
        concerns = intake_data.get("concerns", [])
        profile_text = (
            f" for {skin_type} skin with {', '.join(concerns)} concerns"
            if skin_type or concerns
            else ""
        )

    # Include a short snippet of the user's query to avoid an unused-argument warning
    query_snippet = (
        question[:100] + "..." if question and len(question) > 100 else (question or "")
    )

    # Split the long message across lines so no single source line exceeds 100 chars.
    first_line = (
        "I couldn't find specific products"
        + profile_text
        + ' in our database for the query: "'
        + query_snippet
        + '".'
    )

    message_lines = [
        first_line,
        "Please try:",
        "1. Rephrasing your question",
        "2. Being more specific about your skin concerns",
        "3. Checking if you've completed your skin profile",
        "",
        "I'm here to help with personalized recommendations!",
    ]

    return {
        "answer": "\n\n".join(message_lines),
        "context_summary": (
            'No relevant products found in database for query: "' + query_snippet + '".'
        ),
        "user_profile": _format_profile_summary(intake_data) if intake_data else "",
        "citations": [],
        "used_docs": [],
        "recommendation_confidence": 0.0,
        "routine_suggestion": "",
    }


def _create_manual_response(composed: Dict, intake_data: Dict = None) -> str:
    """Create a manual response when AI generation fails, using intake_data if provided."""
    summary = composed.get("summary", "")
    profile = composed.get("user_profile", "")

    # Use intake_data to build a fallback profile summary if composed doesn't include one.
    if not profile and intake_data:
        try:
            profile = _format_profile_summary(intake_data)
        except (TypeError, AttributeError, ValueError) as e:
            logger.debug("Failed to format profile summary from intake_data: %s", e)
            profile = ""

    response_parts = []
    if profile:
        response_parts.append(
            f"Based on your profile ({profile}), here are my recommendations:"
        )

    if summary:
        response_parts.append(summary)

    response_parts.extend(
        [
            "\n   Important: Always patch test new products and introduce one at a time.",
            "\n   For persistent skin issues, consider consulting a dermatologist.",
        ]
    )

    return "\n\n".join(response_parts)


def _create_error_response(
    question: str, intake_data: Dict = None, error_msg: str = ""
) -> dict:
    """Create an error response with helpful guidance."""
    # Include a snippet of the user's query to avoid an unused-argument warning and aid
    # debugging.
    query_snippet = (
        question[:100] + "..." if question and len(question) > 100 else (question or "")
    )

    error_lines = [
        "I'm experiencing technical difficulties processing your request.",
        "Please try again in a moment, or contact our support team for assistance.",
        "Your skin health is important to us!",
    ]
    # Keep the returned mapping lines short by assembling the long context string
    # from smaller pieces.
    context_summary = (
        'Error occurred while processing query: "'
        + query_snippet
        + '" Details: '
        + (error_msg[:100] if error_msg else "")
        + "..."
    )

    return {
        "answer": " ".join(error_lines),
        "context_summary": context_summary,
        "user_profile": _format_profile_summary(intake_data) if intake_data else "",
        "citations": [],
        "used_docs": [],
        "recommendation_confidence": 0.0,
        "routine_suggestion": "",
    }


def _calculate_confidence(results: List[Dict], intake_data: Dict = None) -> float:
    """Calculate confidence score for recommendations."""
    if not results:
        return 0.0

    # Base confidence on result scores and matches
    result_scores = [r.get("score", 0) for r in results]
    avg_score = sum(result_scores) / len(result_scores) if result_scores else 0

    # Boost confidence if we have intake data
    intake_boost = 0.1 if intake_data and intake_data.get("skin_type") else 0

    # Boost confidence for perfect matches
    perfect_matches = len(
        [r for r in results if r.get("metadata", {}).get("match_type") == "skin_type"]
    )
    match_boost = min(perfect_matches * 0.1, 0.3)

    confidence = min(avg_score + intake_boost + match_boost, 1.0)
    return round(confidence, 2)


def _extract_routine_from_context(context: str) -> str:
    """Extract routine suggestion from context summary."""
    lines = context.split("\n")
    routine_lines = []
    capturing = False

    for line in lines:
        if "SUGGESTED ROUTINE" in line:
            capturing = True
            continue
        if capturing and line.strip():
            if line.startswith(("1.", "2.", "3.", "4.")):
                routine_lines.append(line.strip())
            elif not line.startswith(("•", "-")) and routine_lines:
                break

    return "\n".join(routine_lines) if routine_lines else ""


def _format_profile_summary(intake_data: Dict = None) -> str:
    """Format a concise profile summary."""
    if not intake_data:
        return ""

    parts = []
    if intake_data.get("skin_type"):
        parts.append(intake_data["skin_type"])
    if intake_data.get("sensitive") == "yes":
        parts.append("sensitive")
    if intake_data.get("concerns"):
        concerns = intake_data["concerns"]
        if isinstance(concerns, list):
            parts.extend(concerns[:2])  # Limit to 2 main concerns
        elif isinstance(concerns, str):
            parts.extend(concerns.split(",")[:2])

    return " | ".join(parts[:4])  # Limit total length
