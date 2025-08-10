import os
import httpx
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.api_key = os.getenv("TERMII_API_KEY")
        self.sender_id = os.getenv("TERMII_SENDER_ID", "SolveWithMe")
        self.base_url = "https://api.ng.termii.com/api"
        
        if not self.api_key:
            logger.warning("Termii API key not found. SMS service will be disabled.")
    
    def check_status(self) -> bool:
        """Check if SMS service is available"""
        return self.api_key is not None
    
    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS notification via Termii"""
        if not self.api_key:
            logger.error("Termii API key not configured")
            return False
        
        try:
            # Clean phone number (remove + and ensure Nigerian format)
            clean_number = phone_number.replace("+", "").replace("whatsapp:", "")
            if not clean_number.startswith("234"):
                if clean_number.startswith("0"):
                    clean_number = "234" + clean_number[1:]
                else:
                    clean_number = "234" + clean_number
            
            payload = {
                "to": clean_number,
                "from": self.sender_id,
                "sms": message,
                "type": "plain",
                "api_key": self.api_key,
                "channel": "generic"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sms/send",
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == "ok":
                        logger.info(f"SMS sent successfully to {clean_number}")
                        return True
                    else:
                        logger.error(f"SMS failed: {result.get('message')}")
                        return False
                else:
                    logger.error(f"SMS API error: {response.status_code}")
                    return False
        
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return False
    
    async def send_bulk_sms(self, recipients: List[str], message: str) -> dict:
        """Send bulk SMS to multiple recipients"""
        if not self.api_key:
            logger.error("Termii API key not configured")
            return {"success": 0, "failed": len(recipients)}
        
        success_count = 0
        failed_count = 0
        
        for phone_number in recipients:
            success = await self.send_sms(phone_number, message)
            if success:
                success_count += 1
            else:
                failed_count += 1
        
        return {"success": success_count, "failed": failed_count}
    
    async def send_study_reminder(self, phone_number: str, student_name: str) -> bool:
        """Send daily study reminder SMS"""
        message = f"""
📚 Good morning {student_name}!

Ready for today's math challenge? 

Send any math question to our WhatsApp and get instant help with step-by-step solutions.

💡 Tip: Try asking about topics you're struggling with!

- SolveWithMe Team
        """.strip()
        
        return await self.send_sms(phone_number, message)
    
    async def send_achievement_notification(
        self, 
        phone_number: str, 
        student_name: str, 
        achievement: str
    ) -> bool:
        """Send achievement notification SMS"""
        message = f"""
🎉 Congratulations {student_name}!

You've achieved: {achievement}

Keep up the excellent work! Your dedication to learning math is paying off.

Continue asking questions and helping your peers.

- SolveWithMe Team
        """.strip()
        
        return await self.send_sms(phone_number, message)
    
    async def send_weekly_summary(
        self, 
        phone_number: str, 
        student_name: str, 
        questions_asked: int,
        topics_covered: List[str]
    ) -> bool:
        """Send weekly learning summary SMS"""
        topics_text = ", ".join(topics_covered[:3])
        if len(topics_covered) > 3:
            topics_text += f" and {len(topics_covered) - 3} more"
        
        message = f"""
📊 Weekly Summary for {student_name}

This week you:
• Asked {questions_asked} math questions
• Covered topics: {topics_text}
• Improved your problem-solving skills!

Keep learning! Send more questions via WhatsApp.

- SolveWithMe Team
        """.strip()
        
        return await self.send_sms(phone_number, message)
