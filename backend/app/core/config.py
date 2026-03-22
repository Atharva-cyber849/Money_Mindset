"""
FastAPI Backend Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Money Mindset API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
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
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    
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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
