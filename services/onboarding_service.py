import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from services.whatsapp_service import WhatsAppService
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)

class OnboardingService:
    def __init__(self, whatsapp_service: WhatsAppService, db_service: DatabaseService):
        self.whatsapp_service = whatsapp_service
        self.db_service = db_service
    
    async def start_student_onboarding(self, phone_number: str) -> bool:
        """Start the student onboarding process"""
        try:
            welcome_message = self._get_welcome_message()
            
            success = await self.whatsapp_service.send_message(
                phone_number, 
                welcome_message
            )
            
            if success:
                # Track onboarding start
                user = await self.db_service.get_or_create_user(phone_number)
                await self._log_onboarding_step(user.id, "welcome_sent")
            
            return success
        
        except Exception as e:
            logger.error(f"Error starting onboarding: {str(e)}")
            return False
    
    async def process_onboarding_response(
        self, 
        phone_number: str, 
        message: str, 
        step: str
    ) -> Optional[str]:
        """Process user response during onboarding"""
        try:
            user = await self.db_service.get_or_create_user(phone_number)
            message_lower = message.lower().strip()
            
            if step == "language_selection":
                return await self._handle_language_selection(user.id, message_lower)
            
            elif step == "grade_selection":
                return await self._handle_grade_selection(user.id, message_lower)
            
            elif step == "school_info":
                return await self._handle_school_info(user.id, message)
            
            elif step == "name_collection":
                return await self._handle_name_collection(user.id, message)
            
            elif step == "demo_question":
                return await self._handle_demo_question(user.id, message)
            
            else:
                return await self._complete_onboarding(user.id)
        
        except Exception as e:
            logger.error(f"Error processing onboarding response: {str(e)}")
            return "Sorry, there was an error. Please try again or contact support."
    
    def _get_welcome_message(self) -> str:
        """Get the welcome message"""
        return """
🎓 Welcome to SolveWithMe! 

I'm your AI math tutor, ready to help you master mathematics for WAEC and JAMB exams.

🌍 **Choose your preferred language:**

1️⃣ English
2️⃣ Hausa 
3️⃣ Yoruba
4️⃣ Igbo

Reply with the number (1, 2, 3, or 4) to continue.
        """.strip()
    
    async def _handle_language_selection(self, user_id: int, response: str) -> str:
        """Handle language selection step"""
        language_map = {
            "1": "english",
            "2": "hausa", 
            "3": "yoruba",
            "4": "igbo"
        }
        
        if response in language_map:
            language = language_map[response]
            
            # Update user language preference
            await self._update_user_preference(user_id, "preferred_language", language)
            await self._log_onboarding_step(user_id, "language_selected")
            
            # Return grade selection message in chosen language
            return self._get_grade_selection_message(language)
        else:
            return "Please reply with 1, 2, 3, or 4 to select your language."
    
    async def _handle_grade_selection(self, user_id: int, response: str) -> str:
        """Handle grade level selection"""
        grade_map = {
            "1": "SS1",
            "2": "SS2", 
            "3": "SS3"
        }
        
        if response in grade_map:
            grade = grade_map[response]
            
            # Update user grade level
            await self._update_user_preference(user_id, "grade_level", grade)
            await self._log_onboarding_step(user_id, "grade_selected")
            
            return """
📚 Great! Now tell me about your school.

What's the name of your school?

Type your school name (e.g., "Government Secondary School Lagos")
            """.strip()
        else:
            return "Please reply with 1, 2, or 3 to select your grade level."
    
    async def _handle_school_info(self, user_id: int, school_name: str) -> str:
        """Handle school information collection"""
        # Update user school
        await self._update_user_preference(user_id, "school", school_name)
        await self._log_onboarding_step(user_id, "school_provided")
        
        return """
👋 Finally, what's your name?

This helps me personalize your learning experience.

Type your first name (e.g., "Adebayo")
        """.strip()
    
    async def _handle_name_collection(self, user_id: int, name: str) -> str:
        """Handle name collection"""
        # Update user name
        await self._update_user_preference(user_id, "name", name.title())
        await self._log_onboarding_step(user_id, "name_provided")
        
        return f"""
🎉 Welcome {name.title()}! Setup complete!

Let's try your first question. Here's how it works:

📝 **Send me any math question:**
• Type it out
• Send a photo of the problem
• Record a voice note

Try asking: "Solve for x: 2x + 5 = 13"

Go ahead, ask me anything! 🚀
        """.strip()
    
    async def _handle_demo_question(self, user_id: int, question: str) -> str:
        """Handle the demo question to complete onboarding"""
        await self._log_onboarding_step(user_id, "demo_question_asked")
        
        # This would normally process through the AI service
        # For onboarding, we'll give a quick demo response
        demo_response = """
🔢 **Solving: 2x + 5 = 13**

**Step 1:** Subtract 5 from both sides
2x + 5 - 5 = 13 - 5
2x = 8

**Step 2:** Divide both sides by 2
2x ÷ 2 = 8 ÷ 2
x = 4

✅ **Answer: x = 4**

🎓 **Perfect!** You're now ready to use SolveWithMe!

**What you can do:**
• Ask any math question anytime
• Get step-by-step solutions
• Practice with WAEC/JAMB questions
• Join study discussions with peers

**Tips:**
• Be specific with your questions
• Include any given values or conditions
• Ask for explanations if you need more help

Ready to ace your math exams! 💪
        """.strip()
        
        await self._complete_onboarding_setup(user_id)
        return demo_response
    
    def _get_grade_selection_message(self, language: str) -> str:
        """Get grade selection message in chosen language"""
        messages = {
            "english": """
📚 **Select your grade level:**

1️⃣ SS1 (Senior Secondary 1)
2️⃣ SS2 (Senior Secondary 2) 
3️⃣ SS3 (Senior Secondary 3)

Reply with 1, 2, or 3.
            """.strip(),
            
            "hausa": """
📚 **Zaɓi matakin karatunka:**

1️⃣ SS1 (Senior Secondary 1)
2️⃣ SS2 (Senior Secondary 2)
3️⃣ SS3 (Senior Secondary 3)

Ka amsa da 1, 2, ko 3.
            """.strip(),
            
            "yoruba": """
📚 **Yan ipele eko re:**

1️⃣ SS1 (Senior Secondary 1)
2️⃣ SS2 (Senior Secondary 2)
3️⃣ SS3 (Senior Secondary 3)

Dahun pelu 1, 2, tabi 3.
            """.strip(),
            
            "igbo": """
📚 **Họrọ ọkwa mmụta gị:**

1️⃣ SS1 (Senior Secondary 1)
2️⃣ SS2 (Senior Secondary 2)
3️⃣ SS3 (Senior Secondary 3)

Zaghachi na 1, 2, ma ọ bụ 3.
            """.strip()
        }
        
        return messages.get(language, messages["english"])
    
    async def _update_user_preference(self, user_id: int, field: str, value: str):
        """Update user preference in database"""
        if not self.db_service.pool:
            await self.db_service.init_pool()
        
        try:
            async with self.db_service.pool.acquire() as conn:
                await conn.execute(
                    f"UPDATE users SET {field} = $1, updated_at = $2 WHERE id = $3",
                    value, datetime.utcnow(), user_id
                )
        except Exception as e:
            logger.error(f"Error updating user preference: {str(e)}")
    
    async def _log_onboarding_step(self, user_id: int, step: str):
        """Log onboarding step completion"""
        if not self.db_service.pool:
            await self.db_service.init_pool()
        
        try:
            async with self.db_service.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO user_activities (user_id, activity_type, activity_data)
                    VALUES ($1, $2, $3)
                    """,
                    user_id,
                    "onboarding_step",
                    {"step": step, "timestamp": datetime.utcnow().isoformat()}
                )
        except Exception as e:
            logger.error(f"Error logging onboarding step: {str(e)}")
    
    async def _complete_onboarding_setup(self, user_id: int):
        """Complete the onboarding process"""
        await self._log_onboarding_step(user_id, "onboarding_completed")
        
        # Mark user as fully onboarded
        await self._update_user_preference(user_id, "is_onboarded", "true")
    
    async def get_onboarding_stats(self) -> Dict[str, int]:
        """Get onboarding completion statistics"""
        if not self.db_service.pool:
            await self.db_service.init_pool()
        
        try:
            async with self.db_service.pool.acquire() as conn:
                # Get onboarding completion rates
                total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
                
                completed_onboarding = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM user_activities 
                    WHERE activity_type = 'onboarding_step' 
                    AND activity_data->>'step' = 'onboarding_completed'
                    """
                )
                
                # Get step completion counts
                step_counts = await conn.fetch(
                    """
                    SELECT 
                        activity_data->>'step' as step,
                        COUNT(*) as count
                    FROM user_activities 
                    WHERE activity_type = 'onboarding_step'
                    GROUP BY activity_data->>'step'
                    """
                )
                
                return {
                    "total_users": total_users or 0,
                    "completed_onboarding": completed_onboarding or 0,
                    "completion_rate": round((completed_onboarding or 0) / max(total_users or 1, 1) * 100, 1),
                    "step_completion": {row['step']: row['count'] for row in step_counts}
                }
        
        except Exception as e:
            logger.error(f"Error getting onboarding stats: {str(e)}")
            return {
                "total_users": 0,
                "completed_onboarding": 0,
                "completion_rate": 0.0,
                "step_completion": {}
            }
