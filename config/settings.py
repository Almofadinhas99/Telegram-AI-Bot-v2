import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Telegram Bot Configuration
    telegram_bot_token: str
    telegram_webhook_url: Optional[str] = None
    
    # AI APIs Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None
    replicate_api_token: Optional[str] = None
    fal_api_key: Optional[str] = None
    
    # Database Configuration
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # Payment Configuration
    stripe_publishable_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # Application Configuration
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Pricing Configuration
    profit_margin_min: float = 0.30  # 30%
    profit_margin_max: float = 0.45  # 45%
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

