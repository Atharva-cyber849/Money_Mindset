"""
FastAPI Backend Configuration
"""
import json
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Money Mindset API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    AUTO_CREATE_TABLES: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/moneymindset"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenRouter (OpenAI-compatible API)
    OPENAI_API_KEY: str = ""  # OpenRouter API key
    OPENAI_MODEL: str = "openai/gpt-oss-120b:free"
    OPENAI_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Anthropic
    ANTHROPIC_API_KEY: str = ""  # Anthropic API key
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    # Optional regex for ephemeral preview domains, e.g. ^https://.*\\.vercel\\.app$
    CORS_ALLOW_ORIGIN_REGEX: Optional[str] = None

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        """Allow CORS_ORIGINS to be provided as JSON array or comma-separated string."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                try:
                    parsed = json.loads(stripped)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except Exception:
                    pass
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return value
    
    # Simulation
    MONTE_CARLO_ITERATIONS: int = 10000

    # Market Data APIs
    FINNHUB_API_KEY: str = ""
    FINNHUB_ENABLED: bool = True

    INDIAN_MARKET_API_URL: str = "https://api.example.com"
    INDIAN_MARKET_API_KEY: str = ""
    INDIAN_MARKET_ENABLED: bool = True

    # yfinance Fallback
    YFINANCE_ENABLED: bool = True

    # News API
    NEWSAPI_KEY: Optional[str] = None
    NEWSAPI_ENABLED: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
