import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.core.models import ConversationState, UserPreferences, ChatMessage
from app.core.config import settings

logger = logging.getLogger(__name__)


class SessionService:
    def __init__(self):
        # For now, use in-memory storage. In production, use Redis
        self.sessions: Dict[str, ConversationState] = {}
        self.session_timeout = timedelta(hours=24)  # Sessions expire after 24 hours

    def create_session(self) -> str:
        """Create a new session and return the session ID."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ConversationState(
            session_id=session_id,
            current_step="greeting",
            user_preferences=UserPreferences(),
            conversation_history=[],
            suggested_hobbies=[],
            is_complete=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        logger.info(f"Created new session: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[ConversationState]:
        """Get session by ID."""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        # Check if session has expired
        if datetime.now() - session.created_at > self.session_timeout:
            self.delete_session(session_id)
            return None

        return session

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session with new data."""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]

        # Update specific fields
        if "current_step" in updates:
            session.current_step = updates["current_step"]

        if "user_preferences" in updates:
            # Merge preferences
            prefs = updates["user_preferences"]
            if "likes" in prefs:
                session.user_preferences.likes.extend(prefs["likes"])
            if "dislikes" in prefs:
                session.user_preferences.dislikes.extend(prefs["dislikes"])
            if "personality_traits" in prefs:
                session.user_preferences.personality_traits.extend(
                    prefs["personality_traits"]
                )
            if "lifestyle" in prefs:
                session.user_preferences.lifestyle.update(prefs["lifestyle"])
            if "past_activities" in prefs:
                session.user_preferences.past_activities.extend(
                    prefs["past_activities"]
                )
            if "energy_level" in prefs:
                session.user_preferences.energy_level = prefs["energy_level"]
            if "mood" in prefs:
                session.user_preferences.mood = prefs["mood"]

        if "conversation_history" in updates:
            session.conversation_history = updates["conversation_history"]

        if "suggested_hobbies" in updates:
            session.suggested_hobbies = updates["suggested_hobbies"]

        if "is_complete" in updates:
            session.is_complete = updates["is_complete"]

        session.updated_at = datetime.now()
        logger.info(f"Updated session: {session_id}")
        return True

    def add_message(self, session_id: str, message: str, is_user: bool) -> bool:
        """Add a message to the conversation history."""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        chat_message = ChatMessage(
            content=message, timestamp=datetime.now(), is_user=is_user
        )

        session.conversation_history.append(chat_message)
        session.updated_at = datetime.now()

        logger.info(
            f"Added message to session {session_id}: {'User' if is_user else 'Bot'}"
        )
        return True

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get current session context for AI processing."""
        session = self.get_session(session_id)
        if not session:
            return {}

        return {
            "current_step": session.current_step,
            "user_preferences": session.user_preferences.dict(),
            "conversation_history": [
                {
                    "content": msg.content,
                    "is_user": msg.is_user,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in session.conversation_history[
                    -5:
                ]  # Last 5 messages for context
            ],
            "suggested_hobbies": session.suggested_hobbies,
            "is_complete": session.is_complete,
        }

    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        current_time = datetime.now()
        expired_sessions = [
            session_id
            for session_id, session in self.sessions.items()
            if current_time - session.created_at > self.session_timeout
        ]

        for session_id in expired_sessions:
            self.delete_session(session_id)

        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")


# Global session service instance
session_service = SessionService()
