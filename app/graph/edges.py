import logging
from typing import Dict, Any
from app.graph.state import GraphState, ConversationStep

logger = logging.getLogger(__name__)


def determine_next_step(state: GraphState) -> str:
    """Determine the next step in the conversation flow."""
    current_step = state["current_step"]

    logger.info(f"Determining next step from: {current_step}")

    # Simple linear flow for now
    if current_step == ConversationStep.GREETING:
        return "extract_interests"
    elif current_step == ConversationStep.ASKING_INTERESTS:
        return "extract_dislikes"
    elif current_step == ConversationStep.ASKING_DISLIKES:
        return "extract_lifestyle"
    elif current_step == ConversationStep.ASKING_LIFESTYLE:
        return "generate_suggestions"
    elif current_step == ConversationStep.GENERATING_SUGGESTIONS:
        return "clarification"
    elif current_step == ConversationStep.CLARIFICATION:
        # Check if conversation should continue or end
        if state["is_complete"]:
            return "completion"
        else:
            return "clarification"  # Stay in clarification mode
    elif current_step == ConversationStep.COMPLETE:
        return "completion"
    else:
        return "greeting"  # Default fallback


def should_continue(state: GraphState) -> bool:
    """Determine if the conversation should continue."""
    return state.get("continue_conversation", True) and not state.get(
        "is_complete", False
    )


def route_conversation(state: GraphState) -> str:
    """Route the conversation based on current state."""
    if state.get("is_complete", False):
        return "completion"

    # Check if we have enough information to generate suggestions
    prefs = state.get("user_preferences", {})
    has_likes = bool(prefs.get("likes", []))
    has_dislikes = bool(prefs.get("dislikes", []))
    has_lifestyle = bool(prefs.get("lifestyle", {}))

    current_step = state["current_step"]

    if current_step == ConversationStep.GREETING:
        return "extract_interests"
    elif current_step == ConversationStep.ASKING_INTERESTS:
        if has_likes:
            return "extract_dislikes"
        else:
            return "extract_interests"  # Need more interest information
    elif current_step == ConversationStep.ASKING_DISLIKES:
        if has_dislikes:
            return "extract_lifestyle"
        else:
            return "extract_dislikes"  # Need more dislike information
    elif current_step == ConversationStep.ASKING_LIFESTYLE:
        return "generate_suggestions"
    elif current_step == ConversationStep.GENERATING_SUGGESTIONS:
        return "clarification"
    elif current_step == ConversationStep.CLARIFICATION:
        if state.get("is_complete", False):
            return "completion"
        else:
            return "clarification"
    else:
        return "greeting"  # Default fallback


def check_conversation_flow(state: GraphState) -> Dict[str, Any]:
    """Check and validate conversation flow."""
    current_step = state["current_step"]
    prefs = state.get("user_preferences", {})

    # Validate that we have minimum required information
    validation_result = {
        "is_valid": True,
        "missing_info": [],
        "suggested_next_step": None,
    }

    if current_step == ConversationStep.GENERATING_SUGGESTIONS:
        if not prefs.get("likes", []):
            validation_result["is_valid"] = False
            validation_result["missing_info"].append("likes")
            validation_result["suggested_next_step"] = ConversationStep.ASKING_INTERESTS

        if not prefs.get("dislikes", []):
            validation_result["is_valid"] = False
            validation_result["missing_info"].append("dislikes")
            validation_result["suggested_next_step"] = ConversationStep.ASKING_DISLIKES

    return validation_result
