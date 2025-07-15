from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from app.core.models import ChatRequest, ChatResponse
from app.services.chat_service import chat_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for processing user messages."""
    try:
        response = await chat_service.process_message(request)
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/chat/restart/{session_id}", response_model=ChatResponse)
async def restart_conversation(session_id: str):
    """Restart a conversation for a given session."""
    try:
        response = await chat_service.restart_conversation(session_id)
        return response
    except Exception as e:
        logger.error(f"Error restarting conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/chat/history/{session_id}")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session."""
    try:
        history = chat_service.get_conversation_history(session_id)
        if "error" in history:
            raise HTTPException(status_code=404, detail=history["error"])
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/chat/summary/{session_id}")
async def get_session_summary(session_id: str):
    """Get a summary of the session."""
    try:
        summary = chat_service.get_session_summary(session_id)
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/chat/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    try:
        success = chat_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/chat/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "chat"}


@router.get("/chat/sessions")
async def list_active_sessions():
    """List active sessions (for debugging)."""
    try:
        # This would be useful for monitoring/debugging
        return {"message": "Active sessions endpoint - implement based on your needs"}
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
