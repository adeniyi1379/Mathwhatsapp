import os
import httpx
import logging
from typing import Optional
import tempfile
import whisper

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        # Load Whisper model (using base model for balance of speed/accuracy)
        try:
            self.whisper_model = whisper.load_model("base")
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            self.whisper_model = None
    
    async def voice_to_text(self, audio_url: str) -> str:
        """Convert voice message to text using Whisper"""
        if not self.whisper_model:
            logger.error("Whisper model not available")
            return ""
        
        try:
            # Download audio file
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url)
                response.raise_for_status()
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
                    temp_file.write(response.content)
                    temp_file_path = temp_file.name
                
                # Transcribe using Whisper
                result = self.whisper_model.transcribe(temp_file_path)
                text = result["text"].strip()
                
                # Clean up temporary file
                os.unlink(temp_file_path)
                
                logger.info(f"Transcribed audio: {text[:100]}...")
                return text
        
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return ""
    
    def detect_language_from_audio(self, audio_url: str) -> str:
        """Detect language from audio (using Whisper's language detection)"""
        if not self.whisper_model:
            return "english"
        
        try:
            # This would use Whisper's language detection capability
            # For now, return default
            return "english"
        
        except Exception as e:
            logger.error(f"Error detecting language from audio: {str(e)}")
            return "english"
