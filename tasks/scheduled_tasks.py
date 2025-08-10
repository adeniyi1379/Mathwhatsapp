import asyncio
import logging
from datetime import datetime, time
from typing import Dict, Any
import schedule

from services.notification_service import NotificationService
from services.analytics_service import AnalyticsService
from services.sms_service import SMSService
from services.whatsapp_service import WhatsAppService
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)

class ScheduledTasks:
    def __init__(self):
        self.db_service = DatabaseService()
        self.sms_service = SMSService()
        self.whatsapp_service = WhatsAppService()
        self.notification_service = NotificationService(
            self.sms_service, 
            self.whatsapp_service, 
            self.db_service
        )
        self.analytics_service = AnalyticsService(self.db_service)
        
    async def setup_scheduled_tasks(self):
        """Setup all scheduled tasks"""
        # Daily tasks
        schedule.every().day.at("08:00").do(self._run_async_task, self.send_daily_reminders)
        schedule.every().day.at("18:00").do(self._run_async_task, self.generate_daily_analytics)
        
        # Weekly tasks
        schedule.every().sunday.at("09:00").do(self._run_async_task, self.send_weekly_summaries)
        schedule.every().friday.at("16:00").do(self._run_async_task, self.notify_teachers)
        
        # Monthly tasks
        schedule.every().month.do(self._run_async_task, self.cleanup_old_data)
        
        logger.info("Scheduled tasks configured successfully")
    
    def _run_async_task(self, coro):
        """Helper to run async tasks in schedule"""
        asyncio.create_task(coro())
    
    async def send_daily_reminders(self):
        """Send daily study reminders"""
        try:
            logger.info("Starting daily reminder task")
            await self.notification_service.send_daily_reminders()
            logger.info("Daily reminder task completed")
        except Exception as e:
            logger.error(f"Error in daily reminder task: {str(e)}")
    
    async def send_weekly_summaries(self):
        """Send weekly learning summaries"""
        try:
            logger.info("Starting weekly summary task")
            await self.notification_service.send_weekly_summaries()
            logger.info("Weekly summary task completed")
        except Exception as e:
            logger.error(f"Error in weekly summary task: {str(e)}")
    
    async def notify_teachers(self):
        """Notify teachers about struggling students"""
        try:
            logger.info("Starting teacher notification task")
            await self.notification_service.notify_teachers_of_struggling_students()
            logger.info("Teacher notification task completed")
        except Exception as e:
            logger.error(f"Error in teacher notification task: {str(e)}")
    
    async def generate_daily_analytics(self):
        """Generate and send daily analytics"""
        try:
            logger.info("Starting daily analytics task")
            report = await self.analytics_service.generate_daily_report()
            logger.info(f"Daily analytics generated: {report['platform_metrics']}")
        except Exception as e:
            logger.error(f"Error in daily analytics task: {str(e)}")
    
    async def cleanup_old_data(self):
        """Clean up old data to maintain performance"""
        try:
            logger.info("Starting data cleanup task")
            
            if not self.db_service.pool:
                await self.db_service.init_pool()
            
            async with self.db_service.pool.acquire() as conn:
                # Delete old user activities (older than 6 months)
                six_months_ago = datetime.utcnow() - timedelta(days=180)
                
                deleted_activities = await conn.fetchval(
                    "DELETE FROM user_activities WHERE created_at < $1 RETURNING COUNT(*)",
                    six_months_ago
                )
                
                # Archive old questions and responses (older than 1 year)
                one_year_ago = datetime.utcnow() - timedelta(days=365)
                
                # In a real implementation, you'd move to an archive table
                # For now, just log what would be archived
                old_questions = await conn.fetchval(
                    "SELECT COUNT(*) FROM questions WHERE created_at < $1",
                    one_year_ago
                )
                
                logger.info(f"Cleanup completed: {deleted_activities} activities deleted, {old_questions} questions ready for archiving")
        
        except Exception as e:
            logger.error(f"Error in cleanup task: {str(e)}")
    
    def run_scheduler(self):
        """Run the task scheduler"""
        while True:
            schedule.run_pending()
            asyncio.sleep(60)  # Check every minute
