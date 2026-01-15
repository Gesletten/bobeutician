"""
QA endpoint placeholders
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException
from app.schemas import QARequest, QAResponse

from app.core.generate import generate_answer

router = APIRouter()
logger = logging.getLogger(__name__)


# Reuse `get_db` from `app.db.session` to avoid duplicate code


@router.post("/", response_model=QAResponse)
async def answer_question(req: QARequest):
    """QA endpoint that considers user's intake data for personalized responses"""

    try:
        # Build context information
        context = f"Question received: {req.question}"
        if req.concern:
            context += f" | Concern: {req.concern}"

        if req.intake_data:
            profile_parts = [
                f"Skin: {req.intake_data.get('skin_type', 'unknown')}",
                f"Sensitive: {req.intake_data.get('sensitive', 'unknown')}",
                f"Concerns: {req.intake_data.get('concerns', [])}",
            ]
            context += " | User Profile - " + ", ".join(profile_parts)

        # Generate actual LLM response with intake data
        answer = await generate_answer(req.question, context, req.intake_data)

        return QAResponse(answer=answer, context_summary=context, citations=[])
    except (
        ValueError,
        TypeError,
        RuntimeError,
        HTTPException,
        asyncio.CancelledError,
    ) as e:
        # Log the error and return a safe fallback response
        logger.exception("Error generating answer: %s", e)

        # Fallback response
        context = f"Question received: {req.question}"
        if req.concern:
            context += f" | Concern: {req.concern}"

        if req.intake_data:
            profile_parts = [
                f"Skin: {req.intake_data.get('skin_type', 'unknown')}",
                f"Sensitive: {req.intake_data.get('sensitive', 'unknown')}",
                f"Concerns: {req.intake_data.get('concerns', [])}",
            ]
            context += " | User Profile - " + ", ".join(profile_parts)

        return QAResponse(
            answer="I apologize, but I'm having trouble processing "
            "your request right now. Please try again or contact support.",
            context_summary=context,
            citations=[],
        )
