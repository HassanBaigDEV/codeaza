from typing import Optional, Dict, Any
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIClient:
    def __init__(self):
        self.provider = settings.ai_provider
        self.client = self._initialize_client()

    def _initialize_client(self):
        """Initialize the AI client based on the configured provider."""
        if self.provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key is required")
            return ChatOpenAI(
                openai_api_key=settings.openai_api_key,
                model_name="gpt-3.5-turbo",
                temperature=0.7,
            )
        elif self.provider == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic API key is required")
            return ChatAnthropic(
                anthropic_api_key=settings.anthropic_api_key,
                model="claude-3-sonnet-20240229",
                temperature=0.7,
            )
        elif self.provider == "google":
            if not settings.google_api_key:
                raise ValueError("Google API key is required")
            return ChatGoogleGenerativeAI(
                google_api_key=settings.google_api_key,
                model="gemini-pro",
                temperature=0.7,
            )
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    async def extract_preferences(
        self, user_message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract user preferences from their message."""
        system_prompt = """
        You are an expert at extracting user preferences from conversational text.
        Extract the following information from the user's message:
        - likes: things they explicitly mention enjoying
        - dislikes: things they explicitly mention not enjoying
        - personality_traits: personality indicators (introverted, creative, analytical, etc.)
        - lifestyle: lifestyle indicators (busy, relaxed, outdoors-focused, etc.)
        - past_activities: activities they mention having done before
        - energy_level: their current energy level (low, medium, high)
        - mood: their current mood if mentioned
        
        Return the response as a JSON object. Only include fields that are explicitly mentioned or can be reasonably inferred.
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"User message: {user_message}\nContext: {json.dumps(context)}"
            ),
        ]

        try:
            response = await self.client.ainvoke(messages)
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Error extracting preferences: {e}")
            return {}

    async def generate_response(
        self, user_message: str, context: Dict[str, Any], step: str
    ) -> Dict[str, Any]:
        """Generate a contextual response based on the current conversation step."""
        system_prompts = {
            "greeting": """
            You are a friendly hobby suggestion chatbot. Greet the user warmly and ask about their interests.
            Keep it conversational and encouraging. Ask about what they enjoy doing in their free time.
            """,
            "asking_interests": """
            You are gathering information about the user's interests. Ask follow-up questions to understand:
            - What activities they enjoy
            - What environments they prefer (indoor/outdoor)
            - Their energy levels and preferred time commitments
            Keep the conversation natural and engaging.
            """,
            "asking_dislikes": """
            You are gathering information about what the user dislikes or wants to avoid.
            Ask about activities, environments, or situations they prefer to avoid.
            This helps filter out unsuitable hobby suggestions.
            """,
            "asking_lifestyle": """
            You are gathering information about the user's lifestyle and personality.
            Ask about their schedule, social preferences, and personal characteristics.
            This helps tailor hobby suggestions to their lifestyle.
            """,
            "generating_suggestions": """
            You are generating hobby suggestions based on the user's preferences.
            Provide 3-5 specific hobby suggestions with brief explanations of why each would suit them.
            Make the suggestions personalized and encouraging.
            """,
            "clarification": """
            You are clarifying or refining hobby suggestions based on user feedback.
            Ask follow-up questions or provide alternative suggestions based on their response.
            """,
        }

        system_prompt = system_prompts.get(step, system_prompts["greeting"])

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"User message: {user_message}\nContext: {json.dumps(context)}"
            ),
        ]

        try:
            response = await self.client.ainvoke(messages)
            return {
                "message": response.content,
                "needs_user_input": step != "generating_suggestions",
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "message": "I apologize, but I'm having trouble processing that right now. Could you please try again?",
                "needs_user_input": True,
            }

    async def generate_hobby_suggestions(self, preferences: Dict[str, Any]) -> list:
        """Generate specific hobby suggestions based on user preferences."""
        system_prompt = """
        You are an expert hobby advisor. Based on the user's preferences, generate 3-5 specific hobby suggestions.
        
        For each suggestion, consider:
        - User's likes and dislikes
        - Their personality traits
        - Their lifestyle and available time
        - Their energy level and mood
        - Past activities they've enjoyed
        
        Return a JSON array of hobby suggestions, each with:
        - name: the hobby name
        - description: brief description
        - why_suggested: why this hobby suits their preferences
        - difficulty: beginner/intermediate/advanced
        - time_commitment: low/medium/high
        - cost: free/low/medium/high
        - getting_started_tips: array of 2-3 tips to get started
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User preferences: {json.dumps(preferences)}"),
        ]

        try:
            response = await self.client.ainvoke(messages)
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Error generating hobby suggestions: {e}")
            return []


# Global AI client instance
ai_client = AIClient()
