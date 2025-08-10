import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import asyncio

from services.sms_service import SMSService
from services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, sms_service: SMSService, whatsapp_service: WhatsAppService, db_service):
        self.sms_service = sms_service
        self.whatsapp_service = whatsapp_service
        self.db_service = db_service
    
    async def send_daily_reminders(self):
        """Send daily study reminders to active students"""
        try:
            if not self.db_service.pool:
                await self.db_service.init_pool()
            
            async with self.db_service.pool.acquire() as conn:
                # Get students who were active in the last 3 days but not today
                three_days_ago = datetime.utcnow() - timedelta(days=3)
                today = datetime.utcnow().date()
                
                students = await conn.fetch(
                    """
                    SELECT DISTINCT u.id, u.name, u.phone_number, u.preferred_language
                    FROM users u
                    JOIN questions q ON u.id = q.user_id
                    WHERE q.created_at >= $1 
                    AND u.id NOT IN (
                        SELECT DISTINCT user_id 
                        FROM questions 
                        WHERE DATE(created_at) = $2
                    )
                    AND u.is_active = true
                    """,
                    three_days_ago, today
                )
                
                for student in students:
                    # Send WhatsApp reminder first
                    whatsapp_message = self._create_reminder_message(
                        student['name'], 
                        student['preferred_language']
                    )
                    
                    whatsapp_sent = await self.whatsapp_service.send_message(
                        student['phone_number'],
                        whatsapp_message
                    )
                    
                    # If WhatsApp fails, send SMS backup
                    if not whatsapp_sent and self.sms_service.check_status():
                        await self.sms_service.send_study_reminder(
                            student['phone_number'],
                            student['name']
                        )
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.5)
                
                logger.info(f"Sent daily reminders to {len(students)} students")
        
        except Exception as e:
            logger.error(f"Error sending daily reminders: {str(e)}")
    
    async def send_weekly_summaries(self):
        """Send weekly learning summaries to students"""
        try:
            if not self.db_service.pool:
                await self.db_service.init_pool()
            
            async with self.db_service.pool.acquire() as conn:
                week_ago = datetime.utcnow() - timedelta(days=7)
                
                # Get students with activity this week
                students_data = await conn.fetch(
                    """
                    SELECT 
                        u.id, u.name, u.phone_number, u.preferred_language,
                        COUNT(q.id) as questions_asked,
                        ARRAY_AGG(DISTINCT q.topic) FILTER (WHERE q.topic IS NOT NULL) as topics
                    FROM users u
                    JOIN questions q ON u.id = q.user_id
                    WHERE q.created_at >= $1
                    GROUP BY u.id, u.name, u.phone_number, u.preferred_language
                    HAVING COUNT(q.id) > 0
                    """,
                    week_ago
                )
                
                for student_data in students_data:
                    topics = [t for t in (student_data['topics'] or []) if t]
                    
                    # Send WhatsApp summary
                    summary_message = self._create_weekly_summary_message(
                        student_data['name'],
                        student_data['questions_asked'],
                        topics,
                        student_data['preferred_language']
                    )
                    
                    whatsapp_sent = await self.whatsapp_service.send_message(
                        student_data['phone_number'],
                        summary_message
                    )
                    
                    # SMS backup
                    if not whatsapp_sent and self.sms_service.check_status():
                        await self.sms_service.send_weekly_summary(
                            student_data['phone_number'],
                            student_data['name'],
                            student_data['questions_asked'],
                            topics
                        )
                    
                    await asyncio.sleep(0.5)
                
                logger.info(f"Sent weekly summaries to {len(students_data)} students")
        
        except Exception as e:
            logger.error(f"Error sending weekly summaries: {str(e)}")
    
    async def notify_teachers_of_struggling_students(self):
        """Notify teachers about students who might need extra help"""
        try:
            if not self.db_service.pool:
                await self.db_service.init_pool()
            
            async with self.db_service.pool.acquire() as conn:
                week_ago = datetime.utcnow() - timedelta(days=7)
                
                # Find students with low success rates
                struggling_students = await conn.fetch(
                    """
                    SELECT 
                        u.name, u.school, u.grade_level,
                        COUNT(q.id) as questions_asked,
                        AVG(r.confidence_score) as avg_confidence
                    FROM users u
                    JOIN questions q ON u.id = q.user_id
                    JOIN responses r ON q.id = r.question_id
                    WHERE q.created_at >= $1
                    GROUP BY u.id, u.name, u.school, u.grade_level
                    HAVING COUNT(q.id) >= 3 AND AVG(r.confidence_score) < 0.5
                    """,
                    week_ago
                )
                
                if not struggling_students:
                    return
                
                # Group by school
                schools_data = {}
                for student in struggling_students:
                    school = student['school']
                    if school not in schools_data:
                        schools_data[school] = []
                    schools_data[school].append(student)
                
                # Notify teachers for each school
                for school, students in schools_data.items():
                    # Get teacher moderators for this school
                    teachers = await conn.fetch(
                        """
                        SELECT u.phone_number, u.name
                        FROM teacher_moderators tm
                        JOIN users u ON tm.user_id = u.id
                        JOIN schools s ON tm.school_id = s.id
                        WHERE s.name = $1 AND tm.is_active = true
                        """,
                        school
                    )
                    
                    if teachers:
                        message = self._create_teacher_alert_message(school, students)
                        
                        for teacher in teachers:
                            await self.whatsapp_service.send_message(
                                teacher['phone_number'],
                                message
                            )
                
                logger.info(f"Notified teachers about {len(struggling_students)} struggling students")
        
        except Exception as e:
            logger.error(f"Error notifying teachers: {str(e)}")
    
    def _create_reminder_message(self, name: str, language: str) -> str:
        """Create personalized reminder message"""
        messages = {
            "english": f"""
🌅 Good morning {name}!

Ready to tackle some math problems today? 

💡 Quick tip: Try asking about any topic you're preparing for - algebra, geometry, calculus, or any WAEC/JAMB question!

Send your question now and get instant help! 📚

- Your SolveWithMe Team
            """.strip(),
            
            "hausa": f"""
🌅 Barka da safiya {name}!

Kana shirye ka magance wasu matsalolin lissafi yau?

💡 Shawara: Ka tambaya game da kowane batu da kake shirye-shirye - algebra, geometry, calculus, ko kowace tambayar WAEC/JAMB!

Aika tambayarka yanzu ka samu taimako nan take! 📚

- Tawagar SolveWithMe
            """.strip(),
            
            "yoruba": f"""
🌅 E ku aaro {name}!

Ṣe o ti ṣetan lati koju awọn iṣoro mathematics loni?

💡 Imọran: Beere nipa eyikeyi koko ti o n gbero fun - algebra, geometry, calculus, tabi eyikeyi ibeere WAEC/JAMB!

Fi ibeere rẹ ranṣẹ ni bayi ki o gba iranlọwọ lẹsẹkẹsẹ! 📚

- Ẹgbẹ SolveWithMe rẹ
            """.strip(),
            
            "igbo": f"""
🌅 Ụtụtụ ọma {name}!

Ị dị njikere ịdozi ụfọdụ nsogbu mgbakọ na mwepụ taa?

💡 Ndụmọdụ: Jụọ maka isiokwu ọ bụla ị na-akwado - algebra, geometry, calculus, ma ọ bụ ajụjụ WAEC/JAMB ọ bụla!

Ziga ajụjụ gị ugbu a weta enyemaka ozugbo! 📚

- Ndị otu SolveWithMe gị
            """.strip()
        }
        
        return messages.get(language, messages["english"])
    
    def _create_weekly_summary_message(
        self, 
        name: str, 
        questions_count: int, 
        topics: List[str], 
        language: str
    ) -> str:
        """Create weekly summary message"""
        topics_text = ", ".join(topics[:3]) if topics else "various topics"
        if len(topics) > 3:
            topics_text += f" and {len(topics) - 3} more"
        
        messages = {
            "english": f"""
📊 Weekly Summary for {name}

🎯 This week you achieved:
• {questions_count} math questions solved
• Covered: {topics_text}
• Improved problem-solving skills!

🚀 Keep up the great work! Your dedication is paying off.

Ready for more challenges? Send your next question! 💪

- SolveWithMe Team
            """.strip(),
            
            "hausa": f"""
📊 Taƙaitaccen Mako na {name}

🎯 A wannan mako ka cimma:
• Tambayoyin lissafi {questions_count} da aka magance
• An rufe: {topics_text}
• Inganta ƙwarewar magance matsala!

🚀 Ci gaba da kyakkyawan aiki! Himmarki tana ba da sakamako.

Kana shirye don ƙarin ƙalubale? Aika tambayarka ta gaba! 💪

- Tawagar SolveWithMe
            """.strip()
        }
        
        return messages.get(language, messages["english"])
    
    def _create_teacher_alert_message(self, school: str, students: List[Dict]) -> str:
        """Create teacher alert message for struggling students"""
        student_list = "\n".join([
            f"• {s['name']} ({s['grade_level']}) - {s['questions_asked']} questions, {s['avg_confidence']:.1%} success rate"
            for s in students[:5]
        ])
        
        return f"""
🚨 Teacher Alert - {school}

The following students may need extra support:

{student_list}

These students have been asking questions but showing lower success rates. Consider:
• One-on-one review sessions
• Peer tutoring arrangements  
• Focus on fundamental concepts

Reply DETAILS for more information.

- SolveWithMe Analytics
        """.strip()
