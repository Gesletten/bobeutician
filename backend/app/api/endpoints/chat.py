"""
Chat endpoint for skincare recommendations with intake form integration
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.schemas import ChatRequest, ChatResponse
from app.db.session import get_db
from app.core.rag_pipeline import run_pipeline
from app.core.generate import generate_answer
from app.core.prompts import build_freeform_chat_prompt


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ask", response_model=ChatResponse)
async def chat_ask(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint that integrates intake form data with RAG pipeline.

    Accepts:
    - question: User's natural language question
    - intake_data: Optional intake form responses
    - concern: Optional additional concern
    """
    try:
        logger.info("Received chat request: %s...", request.question[:100])

        # Try SQL-backed retrieval pipeline
        try:
            result = await run_pipeline(
                question=request.question,
                db_session=db,
                intake_data=request.intake_data,
                concern=request.concern,
                k=8,
            )

            # Log for monitoring
            confidence = result.get("recommendation_confidence", 0)
            logger.info("Generated response with confidence: %s", confidence)

            return ChatResponse(
                answer=result["answer"],
                context_summary=result["context_summary"],
                user_profile=result.get("user_profile", ""),
                citations=result["citations"],
                recommendation_confidence=confidence,
                routine_suggestion=result.get("routine_suggestion", ""),
                conversation_id=request.conversation_id,  # Pass through for frontend state
            )
        except (SQLAlchemyError, RuntimeError, ValueError) as pipeline_error:
            logger.warning(
                "Retrieval pipeline failed, using direct LLM: %s", pipeline_error
            )

            # Fallback to direct LLM call with intake context
            context = f"User question: {request.question}"
            if request.intake_data:
                skin_type = request.intake_data.get("skin_type", "unknown")
                sensitive = request.intake_data.get("sensitive", "unknown")
                concerns = request.intake_data.get("concerns", [])
                profile_parts = [
                    f"Skin Type: {skin_type}",
                    f"Sensitive: {sensitive}",
                    f"Concerns: {', '.join(concerns) if concerns else 'none'}",
                ]
                context += "\nUser Profile: " + ", ".join(profile_parts)

            if request.concern:
                context += f"\nAdditional concern: {request.concern}"

            # Use direct LLM generation
            answer = await generate_answer(
                request.question, context, request.intake_data
            )

            # Build user_profile safely to avoid multiline f-string parsing issues
            if request.intake_data:
                _skin = request.intake_data.get("skin_type", "unknown")
            else:
                _skin = "unknown"
            user_profile_value = f"Skin: {_skin}"

            return ChatResponse(
                answer=answer,
                context_summary=context,
                user_profile=user_profile_value,
                citations=[],
                recommendation_confidence=0.5,
                routine_suggestion="",
                conversation_id=request.conversation_id,
            )

    except Exception as e:
        logger.error("Chat endpoint error: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="I'm sorry, I'm having trouble processing your request. Please try again.",
        ) from e


@router.post("/intake")
async def submit_intake_form(intake_data: dict):
    """Intake form submission endpoint"""
    try:
        # Validate intake data (basic validation)
        required_fields = ["skin_type", "sensitive"]
        for field in required_fields:
            if field not in intake_data:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        # Validate skin type
        valid_skin_types = ["oily", "dry", "normal", "combination", "sensitive"]
        if intake_data["skin_type"].lower() not in valid_skin_types:
            raise HTTPException(status_code=400, detail="Invalid skin type")

        # Validate sensitive field
        if intake_data["sensitive"] not in ["yes", "no"]:
            raise HTTPException(
                status_code=400, detail="Sensitive field must be 'yes' or 'no'"
            )

        # Log successful submission
        logger.info("Intake form submitted: %s", intake_data)

        intake_id = f"intake_{intake_data.get('skin_type', 'unknown')}_{len(str(intake_data))}"
        return {
            "status": "success",
            "message": "Intake form saved successfully",
            "intake_id": intake_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Intake form submission error: %s", e)
        raise HTTPException(status_code=500, detail="Failed to process intake form") from e


@router.post("/direct")
async def direct_chat(request: dict):
    """
    Direct LLM chat endpoint - free-form conversational responses like ChatGPT.
    No structured format, just natural conversation.
    """
    try:
        question = request.get("question", "")
        conversation_history = request.get("conversation_history", "")

        if not question.strip():
            raise HTTPException(status_code=400, detail="Question is required")

        logger.info("Direct chat request: %s...", question[:100])

        # Generate free-form conversational prompt
        prompt = build_freeform_chat_prompt(question, conversation_history)

        # Generate answer using the conversational prompt
        answer = await generate_answer(question, "", prompt=prompt)

        logger.info("Generated free-form chat response")

        return {
            "answer": answer,
            "mode": "freeform_chat",
            "conversation_id": request.get("conversation_id"),
        }

    except Exception as e:
        logger.error("Direct chat error: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="I'm sorry, I'm having trouble with that question. Please try again.",
        ) from e


@router.get("/health")
async def health_check():
    """Health check endpoint for chat service."""
    return {"status": "healthy", "service": "chat"}
