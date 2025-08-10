import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # Twilio WhatsApp
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_whatsapp_number: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    
    # Termii SMS
    termii_api_key: str = os.getenv("TERMII_API_KEY", "")
    termii_sender_id: str = os.getenv("TERMII_SENDER_ID", "SolveWithMe")
    
    # Retool Analytics
    retool_webhook_url: Optional[str] = os.getenv("RETOOL_WEBHOOK_URL")
    
    # OpenAI (optional)
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"
    
    # Railway
    port: int = int(os.getenv("PORT", 8000))
    
    # Redis (for caching and task queue)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Feature flags
    enable_sms_notifications: bool = os.getenv("ENABLE_SMS_NOTIFICATIONS", "true").lower() == "true"
    enable_voice_processing: bool = os.getenv("ENABLE_VOICE_PROCESSING", "true").lower() == "true"
    enable_image_processing: bool = os.getenv("ENABLE_IMAGE_PROCESSING", "true").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings()
