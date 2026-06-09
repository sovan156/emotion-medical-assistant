from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Emotion-Aware Medical Assistant"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "emotion_medical_assistant"

    # Ollama settings (replaces OpenAI)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma:2b"
    OLLAMA_TIMEOUT: int = 120

    HF_MODEL_NAME: str = "j-hartmann/emotion-english-distilroberta-base"
    WHISPER_MODEL_SIZE: str = "base"

    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    ENABLE_VOICE_EMOTION: bool = False
    ENABLE_MULTILINGUAL: bool = True

    @property
    def cors_origins(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.ALLOWED_ORIGINS.split(",")
        ]

    class Config:
        env_file = ".env"


settings = Settings()
