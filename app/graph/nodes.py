import logging
from typing import Dict, Any
from app.graph.state import GraphState, ConversationStep, MessageType
from app.utils.ai_client import ai_client
from app.services.session_service import session_service

logger = logging.getLogger(__name__)


async def greeting_node(state: GraphState) -> GraphState:
    """Handle the initial greeting and ask about interests."""
    logger.info(f"Processing greeting for session {state['session_id']}")

    # Generate greeting response
    context = session_service.get_session_context(state["session_id"])
    response = await ai_client.generate_response(
        state["user_message"], context, ConversationStep.GREETING
    )

    # Update state
    state["bot_response"] = response["message"]
    state["current_step"] = ConversationStep.ASKING_INTERESTS
    state["message_type"] = MessageType.GREETING

    return state


async def extract_interests_node(state: GraphState) -> GraphState:
    """Extract user interests from their message."""
    logger.info(f"Extracting interests for session {state['session_id']}")

    # Extract preferences from user message
    context = session_service.get_session_context(state["session_id"])
    preferences = await ai_client.extract_preferences(state["user_message"], context)

    # Update state with extracted preferences
    if preferences:
        state["user_preferences"].update(preferences)

    # Generate response asking about dislikes
    response = await ai_client.generate_response(
        state["user_message"], context, ConversationStep.ASKING_DISLIKES
    )

    state["bot_response"] = response["message"]
    state["current_step"] = ConversationStep.ASKING_DISLIKES
    state["message_type"] = MessageType.QUESTION

    return state


async def extract_dislikes_node(state: GraphState) -> GraphState:
    """Extract user dislikes from their message."""
    logger.info(f"Extracting dislikes for session {state['session_id']}")

    # Extract preferences from user message
    context = session_service.get_session_context(state["session_id"])
    preferences = await ai_client.extract_preferences(state["user_message"], context)

    # Update state with extracted preferences
    if preferences:
        state["user_preferences"].update(preferences)

    # Generate response asking about lifestyle
    response = await ai_client.generate_response(
        state["user_message"], context, ConversationStep.ASKING_LIFESTYLE
    )

    state["bot_response"] = response["message"]
    state["current_step"] = ConversationStep
