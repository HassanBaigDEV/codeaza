import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # AI Configuration
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    ai_provider: str = "google"  # or "anthropic" or "google"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0

    # Application Configuration
    app_name: str = "Hobby Suggestion Chatbot"
    debug: bool = True
    log_level: str = "INFO"

    # CORS Configuration
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
