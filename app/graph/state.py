from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph
from app.core.models import UserPreferences, ChatMessage


class GraphState(TypedDict):
    """State for the LangGraph workflow."""

    # Session information
    session_id: str

    # Current user message
    user_message: str

    # Bot response
    bot_response: str

    # Current step in the conversation
    current_step: str

    # User preferences collected so far
    user_preferences: Dict[str, Any]

    # Conversation history
    conversation_history: List[Dict[str, Any]]

    # Generated hobby suggestions
    hobby_suggestions: List[Dict[str, Any]]

    # Whether the conversation is complete
    is_complete: bool

    # Additional context for AI processing
    context: Dict[str, Any]

    # Message type for response formatting
    message_type: str

    # Whether to continue the conversation
    continue_conversation: bool


class ConversationStep:
    """Constants for conversation steps."""

    GREETING = "greeting"
    ASKING_INTERESTS = "asking_interests"
    ASKING_DISLIKES = "asking_dislikes"
    ASKING_LIFESTYLE = "asking_lifestyle"
    GENERATING_SUGGESTIONS = "generating_suggestions"
    CLARIFICATION = "clarification"
    COMPLETE = "complete"


class MessageType:
    """Constants for message types."""

    GREETING = "greeting"
    QUESTION = "question"
    SUGGESTION = "suggestion"
    FINAL = "final"
    CLARIFICATION = "clarification"


def create_initial_state(session_id: str, user_message: str) -> GraphState:
    """Create initial state for the graph."""
    return GraphState(
        session_id=session_id,
        user_message=user_message,
        bot_response="",
        current_step=ConversationStep.GREETING,
        user_preferences={},
        conversation_history=[],
        hobby_suggestions=[],
        is_complete=False,
        context={},
        message_type=MessageType.GREETING,
        continue_conversation=True,
    )
