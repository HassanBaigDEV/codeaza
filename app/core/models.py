from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    QUESTION = "question"
    SUGGESTION = "suggestion"
    FINAL = "final"
    GREETING = "greeting"
    CLARIFICATION = "clarification"


class ChatMessage(BaseModel):
    content: str = Field(..., description="The message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    is_user: bool = Field(
        ..., description="True if message is from user, False if from bot"
    )


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field(None, description="Session ID for context")


class ChatResponse(BaseModel):
    message: str = Field(..., description="Bot's response message")
    message_type: MessageType = Field(..., description="Type of message")
    session_id: str = Field(..., description="Session ID")
    suggestions: Optional[List[str]] = Field(
        None, description="List of hobby suggestions"
    )
    is_complete: bool = Field(False, description="Whether the conversation is complete")
    context: Optional[Dict[str, Any]] = Field(
        None, description="Current conversation context"
    )


class UserPreferences(BaseModel):
    likes: List[str] = Field(default_factory=list)
    dislikes: List[str] = Field(default_factory=list)
    personality_traits: List[str] = Field(default_factory=list)
    lifestyle: Dict[str, Any] = Field(default_factory=dict)
    past_activities: List[str] = Field(default_factory=list)
    energy_level: Optional[str] = Field(None)
    mood: Optional[str] = Field(None)


class ConversationState(BaseModel):
    session_id: str
    current_step: str = "greeting"
    user_preferences: UserPreferences = Field(default_factory=UserPreferences)
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    suggested_hobbies: List[str] = Field(default_factory=list)
    is_complete: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class HobbyCategory(BaseModel):
    name: str
    description: str
    keywords: List[str]
    energy_level: str  # low, medium, high
    environment: str  # indoor, outdoor, both
    social_aspect: str  # solo, group, both


class HobbySuggestion(BaseModel):
    name: str
    description: str
    category: str
    difficulty: str  # beginner, intermediate, advanced
    time_commitment: str  # low, medium, high
    cost: str  # free, low, medium, high
    why_suggested: str
    getting_started_tips: List[str]
