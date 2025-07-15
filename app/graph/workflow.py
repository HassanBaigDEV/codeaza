import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.graph.state import GraphState, ConversationStep, create_initial_state
from app.graph.nodes import (
    greeting_node,
    extract_interests_node,
    extract_dislikes_node,
    extract_lifestyle_node,
    generate_suggestions_node,
    clarification_node,
    completion_node,
)
from app.graph.edges import route_conversation, should_continue

logger = logging.getLogger(__name__)


class HobbyWorkflow:
    """Main workflow class for the hobby suggestion chatbot."""

    def __init__(self):
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow."""
        # Create the graph
        workflow = StateGraph(GraphState)

        # Add nodes
        workflow.add_node("greeting", greeting_node)
        workflow.add_node("extract_interests", extract_interests_node)
        workflow.add_node("extract_dislikes", extract_dislikes_node)
        workflow.add_node("extract_lifestyle", extract_lifestyle_node)
        workflow.add_node("generate_suggestions", generate_suggestions_node)
        workflow.add_node("clarification", clarification_node)
        workflow.add_node("completion", completion_node)

        # Set entry point
        workflow.set_entry_point("greeting")

        # Add edges with routing logic
        workflow.add_conditional_edges(
            "greeting",
            route_conversation,
            {"extract_interests": "extract_interests", "completion": "completion"},
        )

        workflow.add_conditional_edges(
            "extract_interests",
            route_conversation,
            {
                "extract_dislikes": "extract_dislikes",
                "extract_interests": "extract_interests",
                "completion": "completion",
            },
        )

        workflow.add_conditional_edges(
            "extract_dislikes",
            route_conversation,
            {
                "extract_lifestyle": "extract_lifestyle",
                "extract_dislikes": "extract_dislikes",
                "completion": "completion",
            },
        )

        workflow.add_conditional_edges(
            "extract_lifestyle",
            route_conversation,
            {
                "generate_suggestions": "generate_suggestions",
                "completion": "completion",
            },
        )

        workflow.add_conditional_edges(
            "generate_suggestions",
            route_conversation,
            {"clarification": "clarification", "completion": "completion"},
        )

        workflow.add_conditional_edges(
            "clarification",
            route_conversation,
            {"clarification": "clarification", "completion": "completion"},
        )

        # End the workflow
        workflow.add_edge("completion", END)

        return workflow.compile()

    async def process_message(
        self, session_id: str, user_message: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process a user message through the workflow."""
        try:
            # Create initial state
            if context and context.get("current_step"):
                # Continue existing conversation
                state = GraphState(
                    session_id=session_id,
                    user_message=user_message,
                    bot_response="",
                    current_step=context["current_step"],
                    user_preferences=context.get("user_preferences", {}),
                    conversation_history=context.get("conversation_history", []),
                    hobby_suggestions=context.get("hobby_suggestions", []),
                    is_complete=context.get("is_complete", False),
                    context=context,
                    message_type="question",
                    continue_conversation=not context.get("is_complete", False),
                )
            else:
                # Start new conversation
                state = create_initial_state(session_id, user_message)

            # Run the workflow
            result = await self.graph.ainvoke(state)

            # Return the result
            return {
                "bot_response": result["bot_response"],
                "message_type": result["message_type"],
                "current_step": result["current_step"],
                "user_preferences": result["user_preferences"],
                "hobby_suggestions": result.get("hobby_suggestions", []),
                "is_complete": result["is_complete"],
                "continue_conversation": result["continue_conversation"],
            }

        except Exception as e:
            logger.error(f"Error processing message in workflow: {e}")
            return {
                "bot_response": "I apologize, but I encountered an error processing your message. Let's try again.",
                "message_type": "question",
                "current_step": "greeting",
                "user_preferences": {},
                "hobby_suggestions": [],
                "is_complete": False,
                "continue_conversation": True,
            }


# Global workflow instance
hobby_workflow = HobbyWorkflow()
