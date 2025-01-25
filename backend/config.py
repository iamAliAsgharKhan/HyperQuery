# backend/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    DATABASE_PATH: str = "ecommerce.db"
    MAX_QUERY_LENGTH: int = 500
    CORS_ORIGINS: list = ["*"]
    ALLOWED_OPERATIONS: list = ["SELECT", "PRAGMA"]
settings = Settings()