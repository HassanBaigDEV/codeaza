import logging
from typing import Dict, Any, Optional
from app.graph.workflow import hobby_workflow
from app.services.session_service import session_service
from app.core.models import ConversationState

logger = logging.getLogger(__name__)


class LangGraphService:
    """Service for managing LangGraph workflow execution."""

    def __init__(self):
        self.workflow = hobby_workflow

    async def process_chat_message(
        self, session_id: str, user_message: str
    ) -> Dict[str, Any]:
        """Process a chat message through the LangGraph workflow."""
        try:
            # Get current session context
            context = session_service.get_session_context(session_id)

            # Process message through workflow
            result = await self.workflow.process_message(
                session_id=session_id, user_message=user_message, context=context
            )

            # Update session with new information
            session_updates = {
                "current_step": result["current_step"],
                "user_preferences": result["user_preferences"],
                "suggested_hobbies": result.get("hobby_suggestions", []),
                "is_complete": result["is_complete"],
            }

            # Update session
            session_service.update_session(session_id, session_updates)

            # Add messages to conversation history
            session_service.add_message(session_id, user_message, is_user=True)
            session_service.add_message(
                session_id, result["bot_response"], is_user=False
            )

            return {
                "success": True,
                "bot_response": result["bot_response"],
                "message_type": result["message_type"],
                "current_step": result["current_step"],
                "hobby_suggestions": result.get("hobby_suggestions", []),
                "is_complete": result["is_complete"],
                "continue_conversation": result["continue_conversation"],
            }

        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return {
                "success": False,
                "bot_response": "I apologize, but I encountered an error. Let's try starting over.",
                "message_type": "question",
                "current_step": "greeting",
                "hobby_suggestions": [],
                "is_complete": False,
                "continue_conversation": True,
            }

    async def restart_conversation(self, session_id: str) -> Dict[str, Any]:
        """Restart the conversation for a session."""
        try:
            # Reset session to initial state
            session_updates = {
                "current_step": "greeting",
                "user_preferences": {},
                "conversation_history": [],
                "suggested_hobbies": [],
                "is_complete": False,
            }

            session_service.update_session(session_id, session_updates)

            # Generate greeting message
            greeting_message = "Hello! I'm here to help you discover new hobbies that match your interests. What kinds of activities do you enjoy or have you always wanted to try?"

            # Add greeting to conversation history
            session_service.add_message(session_id, greeting_message, is_user=False)

            return {
                "success": True,
                "bot_response": greeting_message,
                "message_type": "greeting",
                "current_step": "greeting",
                "hobby_suggestions": [],
                "is_complete": False,
                "continue_conversation": True,
            }

        except Exception as e:
            logger.error(f"Error restarting conversation: {e}")
            return {
                "success": False,
                "bot_response": "I apologize, but I encountered an error restarting the conversation.",
                "message_type": "question",
                "current_step": "greeting",
                "hobby_suggestions": [],
                "is_complete": False,
                "continue_conversation": True,
            }

    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the current conversation state."""
        session = session_service.get_session(session_id)
        if not session:
            return {"error": "Session not found"}

        return {
            "session_id": session_id,
            "current_step": session.current_step,
            "user_preferences": session.user_preferences.dict(),
            "suggested_hobbies": session.suggested_hobbies,
            "is_complete": session.is_complete,
            "message_count": len(session.conversation_history),
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
        }


# Global LangGraph service instance
langgraph_service = LangGraphService()
