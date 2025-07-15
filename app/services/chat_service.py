import logging
from typing import Dict, Any, Optional
from app.core.models import ChatRequest, ChatResponse, MessageType
from app.services.session_service import session_service
from app.services.langgraph_service import langgraph_service

logger = logging.getLogger(__name__)


class ChatService:
    """Main chat service that orchestrates the conversation flow."""

    def __init__(self):
        self.session_service = session_service
        self.langgraph_service = langgraph_service

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message and return a response."""
        try:
            # Get or create session
            session_id = request.session_id
            if not session_id:
                session_id = self.session_service.create_session()

            # Ensure session exists
            session = self.session_service.get_session(session_id)
            if not session:
                session_id = self.session_service.create_session()
                session = self.session_service.get_session(session_id)

            # Process message through LangGraph
            result = await self.langgraph_service.process_chat_message(
                session_id=session_id, user_message=request.message
            )

            if not result["success"]:
                # Handle error case
                return ChatResponse(
                    message=result["bot_response"],
                    message_type=MessageType.QUESTION,
                    session_id=session_id,
                    suggestions=None,
                    is_complete=False,
                    context=None,
                )

            # Map message type
            message_type_map = {
                "greeting": MessageType.GREETING,
                "question": MessageType.QUESTION,
                "suggestion": MessageType.SUGGESTION,
                "final": MessageType.FINAL,
                "clarification": MessageType.CLARIFICATION,
            }

            message_type = message_type_map.get(
                result["message_type"], MessageType.QUESTION
            )

            # Format hobby suggestions
            suggestions = None
            if result.get("hobby_suggestions"):
                suggestions = [
                    suggestion.get("name", str(suggestion))
                    for suggestion in result["hobby_suggestions"]
                ]

            # Get current context
            context = self.session_service.get_session_context(session_id)

            return ChatResponse(
                message=result["bot_response"],
                message_type=message_type,
                session_id=session_id,
                suggestions=suggestions,
                is_complete=result["is_complete"],
                context=context,
            )

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Create fallback session if needed
            if not request.session_id:
                session_id = self.session_service.create_session()
            else:
                session_id = request.session_id

            return ChatResponse(
                message="I apologize, but I encountered an error. Let's try again.",
                message_type=MessageType.QUESTION,
                session_id=session_id,
                suggestions=None,
                is_complete=False,
                context=None,
            )

    async def restart_conversation(self, session_id: str) -> ChatResponse:
        """Restart the conversation for a given session."""
        try:
            # Restart conversation through LangGraph service
            result = await self.langgraph_service.restart_conversation(session_id)

            if not result["success"]:
                return ChatResponse(
                    message=result["bot_response"],
                    message_type=MessageType.QUESTION,
                    session_id=session_id,
                    suggestions=None,
                    is_complete=False,
                    context=None,
                )

            # Get updated context
            context = self.session_service.get_session_context(session_id)

            return ChatResponse(
                message=result["bot_response"],
                message_type=MessageType.GREETING,
                session_id=session_id,
                suggestions=None,
                is_complete=False,
                context=context,
            )

        except Exception as e:
            logger.error(f"Error restarting conversation: {e}")
            return ChatResponse(
                message="I apologize, but I encountered an error restarting the conversation.",
                message_type=MessageType.QUESTION,
                session_id=session_id,
                suggestions=None,
                is_complete=False,
                context=None,
            )

    def get_conversation_history(self, session_id: str) -> Dict[str, Any]:
        """Get the conversation history for a session."""
        session = self.session_service.get_session(session_id)
        if not session:
            return {"error": "Session not found"}

        return {
            "session_id": session_id,
            "conversation_history": [
                {
                    "content": msg.content,
                    "is_user": msg.is_user,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in session.conversation_history
            ],
            "current_step": session.current_step,
            "is_complete": session.is_complete,
        }

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the session."""
        return self.langgraph_service.get_conversation_summary(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        return self.session_service.delete_session(session_id)


# Global chat service instance
chat_service = ChatService()
