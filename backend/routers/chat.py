"""
Chat Router - LLM-backed chat API endpoints
"""

from fastapi import APIRouter, HTTPException
from models.chat import ChatRequest, ChatResponse
from services.ai_service import get_ai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get an LLM response with constraint awareness.
    
    The constraints are injected into the system prompt so the LLM
    is aware of user requirements when generating responses.
    """
    try:
        ai_service = get_ai_service()
        
        # Convert Pydantic models to dicts for the service
        constraints = [c.model_dump() for c in request.constraints]
        history = [m.model_dump() for m in request.history]
        
        # Get LLM response
        content = await ai_service.chat(
            message=request.message,
            constraints=constraints,
            history=history
        )
        
        return ChatResponse(
            content=content,
            constraint_violations=[],  # TODO: Add violation detection
            model_used=ai_service.model
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")


@router.post("/chat/test")
async def test_chat():
    """Test endpoint to verify LLM connection."""
    try:
        ai_service = get_ai_service()
        response = await ai_service.chat(
            message="Hello, this is a test.",
            constraints=[{"type": "Goal", "label": "Test goal"}],
            history=[]
        )
        return {"status": "ok", "response": response[:100] + "..."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
