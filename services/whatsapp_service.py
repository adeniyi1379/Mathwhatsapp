import os
import httpx
import logging
from typing import Optional
from twilio.rest import Client

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        
        if not all([self.account_sid, self.auth_token]):
            logger.warning("Twilio credentials not found. WhatsApp service will be disabled.")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
    
    def check_status(self) -> bool:
        """Check if WhatsApp service is available"""
        return self.client is not None
    
    async def send_message(self, to_number: str, message: str) -> bool:
        """Send WhatsApp message to user"""
        if not self.client:
            logger.error("WhatsApp client not initialized")
            return False
        
        try:
            # Ensure number has whatsapp: prefix
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            message = self.client.messages.create(
                body=message,
                from_=self.whatsapp_number,
                to=to_number
            )
            
            logger.info(f"Message sent successfully: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            return False
    
    async def send_media_message(
        self, 
        to_number: str, 
        message: str, 
        media_url: str
    ) -> bool:
        """Send WhatsApp message with media attachment"""
        if not self.client:
            logger.error("WhatsApp client not initialized")
            return False
        
        try:
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            message = self.client.messages.create(
                body=message,
                media_url=[media_url],
                from_=self.whatsapp_number,
                to=to_number
            )
            
            logger.info(f"Media message sent successfully: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp media message: {str(e)}")
            return False
    
    async def send_template_message(
        self, 
        to_number: str, 
        template_name: str, 
        parameters: list
    ) -> bool:
        """Send WhatsApp template message (for notifications)"""
        # Implementation for template messages
        # This would be used for structured notifications
        pass
