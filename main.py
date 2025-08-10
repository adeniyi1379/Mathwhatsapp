from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime
import logging

from services.whatsapp_service import WhatsAppService
from services.ai_service import AIService
from services.database_service import DatabaseService
from services.ocr_service import OCRService
from services.voice_service import VoiceService
from models.schemas import (
    WebhookMessage, 
    UserProfile, 
    Question, 
    Response,
    PeerDiscussion
)
from services.sms_service import SMSService
from services.analytics_service import AnalyticsService
from services.notification_service import NotificationService
from tasks.scheduled_tasks import ScheduledTasks
import asyncio
from contextlib import asynccontextmanager
from services.monitoring_service import MonitoringService, start_monitoring_loop
from services.onboarding_service import OnboardingService
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db_service.init_pool()
    await scheduled_tasks.setup_scheduled_tasks()
    
    # Start background task scheduler
    asyncio.create_task(run_background_scheduler())
    asyncio.create_task(start_monitoring_loop(monitoring_service))
    
    yield
    
    # Shutdown
    if db_service.pool:
        await db_service.pool.close()

async def run_background_scheduler():
    """Run scheduled tasks in background"""
    import schedule
    import time
    
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)

app = FastAPI(
    title="SolveWithMe API",
    description="WhatsApp-based interactive math learning platform for Nigerian secondary students",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
whatsapp_service = WhatsAppService()
ai_service = AIService()
db_service = DatabaseService()
ocr_service = OCRService()
voice_service = VoiceService()
sms_service = SMSService()
analytics_service = AnalyticsService(db_service)
notification_service = NotificationService(sms_service, whatsapp_service, db_service)
scheduled_tasks = ScheduledTasks()
monitoring_service = MonitoringService(db_service)
onboarding_service = OnboardingService(whatsapp_service, db_service)

@app.middleware("http")
async def track_response_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Track response time for monitoring
    await monitoring_service.track_response_time(str(request.url.path), process_time)
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/api/monitoring/health")
async def get_detailed_health():
    """Get detailed health status"""
    try:
        health_status = await monitoring_service.get_health_status()
        performance_metrics = await monitoring_service.get_performance_metrics()
        database_metrics = await monitoring_service.get_database_metrics()
        external_services = await monitoring_service.check_external_services()
        
        return {
            "overall_status": health_status["status"],
            "timestamp": health_status["timestamp"],
            "system_metrics": health_status["metrics"],
            "performance_metrics": performance_metrics,
            "database_metrics": database_metrics,
            "external_services": external_services
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/metrics")
async def get_system_metrics():
    """Get system performance metrics"""
    try:
        return await monitoring_service.get_performance_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/onboarding/stats")
async def get_onboarding_statistics():
    """Get onboarding completion statistics"""
    try:
        return await onboarding_service.get_onboarding_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/notifications/send-reminder")
async def send_study_reminder(phone_number: str, student_name: str):
    """Send study reminder to a specific student"""
    try:
        # Try WhatsApp first
        whatsapp_sent = await whatsapp_service.send_message(
            phone_number,
            notification_service._create_reminder_message(student_name, "english")
        )
        
        # Fallback to SMS
        if not whatsapp_sent and sms_service.check_status():
            sms_sent = await sms_service.send_study_reminder(phone_number, student_name)
            return {"status": "success", "method": "sms", "sent": sms_sent}
        
        return {"status": "success", "method": "whatsapp", "sent": whatsapp_sent}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/analytics/student/{user_id}")
async def get_student_analytics_endpoint(user_id: int):
    """Get analytics for a specific student"""
    try:
        analytics = await analytics_service.get_student_analytics(user_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {
            "student_id": analytics.user_id,
            "name": analytics.name,
            "questions_asked": analytics.questions_asked,
            "topics_covered": analytics.topics_covered,
            "success_rate": analytics.success_rate,
            "engagement_score": analytics.engagement_score,
            "last_active": analytics.last_active.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/analytics/school/{school_id}")
async def get_school_analytics_endpoint(school_id: int):
    """Get analytics for a specific school"""
    try:
        analytics = await analytics_service.get_school_analytics(school_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="School not found")
        
        return {
            "school_id": analytics.school_id,
            "school_name": analytics.school_name,
            "total_students": analytics.total_students,
            "active_students": analytics.active_students,
            "questions_this_week": analytics.questions_this_week,
            "top_topics": analytics.top_topics,
            "average_success_rate": analytics.average_success_rate
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/analytics/platform")
async def get_platform_analytics_endpoint():
    """Get comprehensive platform analytics"""
    try:
        analytics = await analytics_service.get_platform_analytics()
        
        return {
            "total_users": analytics.total_users,
            "daily_active_users": analytics.daily_active_users,
            "questions_today": analytics.questions_today,
            "questions_this_week": analytics.questions_this_week,
            "success_rate": analytics.success_rate,
            "popular_topics": analytics.popular_topics,
            "language_distribution": analytics.language_distribution,
            "grade_distribution": analytics.grade_distribution
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    return {
        "message": "SolveWithMe API is running!",
        "status": "active",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": await db_service.check_connection(),
            "whatsapp": whatsapp_service.check_status(),
            "ai": ai_service.check_status()
        }
    }

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    message: WebhookMessage,
    background_tasks: BackgroundTasks
):
    """Handle incoming WhatsApp messages"""
    try:
        logger.info(f"Received message from {message.from_number}: {message.message_type}")
        
        # Process message in background
        background_tasks.add_task(
            process_whatsapp_message,
            message
        )
        
        return {"status": "received"}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_whatsapp_message(message: WebhookMessage):
    """Process WhatsApp message and generate response"""
    try:
        # Get or create user profile
        user = await db_service.get_or_create_user(message.from_number)
        
        # Extract question content based on message type
        question_text = ""
        
        if message.message_type == "text":
            question_text = message.text
        
        elif message.message_type == "image":
            # Extract text from image using OCR
            question_text = await ocr_service.extract_text_from_image(message.media_url)
            
        elif message.message_type == "voice":
            # Convert voice to text
            question_text = await voice_service.voice_to_text(message.media_url)
        
        if not question_text:
            await whatsapp_service.send_message(
                message.from_number,
                "I couldn't understand your question. Please try sending it as text, a clear image, or voice note."
            )
            return
        
        # Detect language (English, Hausa, Yoruba, Igbo)
        detected_language = ai_service.detect_language(question_text)
        
        # Find similar questions from WAEC/JAMB database
        similar_questions = await ai_service.find_similar_questions(question_text)
        
        # Generate AI response
        ai_response = await ai_service.generate_math_solution(
            question_text,
            similar_questions,
            detected_language,
            user.grade_level
        )
        
        # Save question and response to database
        question_record = await db_service.save_question(
            user_id=user.id,
            question_text=question_text,
            question_type=message.message_type,
            language=detected_language
        )
        
        response_record = await db_service.save_response(
            question_id=question_record.id,
            response_text=ai_response.solution,
            confidence_score=ai_response.confidence
        )
        
        # Send response to user
        await whatsapp_service.send_message(
            message.from_number,
            ai_response.solution
        )
        
        # If confidence is low, suggest peer discussion
        if ai_response.confidence < 0.7:
            await suggest_peer_discussion(message.from_number, question_record.id)
        
        # Send follow-up with similar WAEC/JAMB questions
        if similar_questions:
            follow_up = f"\n\n📚 *Similar WAEC/JAMB Questions:*\n"
            for i, q in enumerate(similar_questions[:2], 1):
                follow_up += f"{i}. {q.question}\n"
            
            await whatsapp_service.send_message(
                message.from_number,
                follow_up
            )
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        await whatsapp_service.send_message(
            message.from_number,
            "Sorry, I encountered an error processing your question. Please try again."
        )

async def suggest_peer_discussion(phone_number: str, question_id: int):
    """Suggest peer discussion for complex questions"""
    message = """
🤝 *Need more help?*

This question seems challenging! Would you like to discuss it with other students? 

Reply with:
• *DISCUSS* - Join a study group discussion
• *TEACHER* - Get help from a teacher moderator
• *RETRY* - Try asking the question differently
    """
    
    await whatsapp_service.send_message(phone_number, message)

@app.post("/api/users/register")
async def register_user(user_data: UserProfile):
    """Register a new user"""
    try:
        user = await db_service.create_user(user_data)
        return {"status": "success", "user_id": user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/questions/{user_id}")
async def get_user_questions(user_id: int, limit: int = 10):
    """Get user's question history"""
    try:
        questions = await db_service.get_user_questions(user_id, limit)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/discussions/create")
async def create_discussion(discussion_data: PeerDiscussion):
    """Create a peer discussion group"""
    try:
        discussion = await db_service.create_discussion(discussion_data)
        
        # Notify participants via WhatsApp
        for participant in discussion.participants:
            await whatsapp_service.send_message(
                participant.phone_number,
                f"🎓 You've been invited to discuss: {discussion.question_preview}\n\nReply *JOIN* to participate!"
            )
        
        return {"status": "success", "discussion_id": discussion.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/analytics/dashboard")
async def get_analytics():
    """Get platform analytics for teachers/admins"""
    try:
        stats = await db_service.get_platform_stats()
        return {
            "total_users": stats.total_users,
            "questions_today": stats.questions_today,
            "active_discussions": stats.active_discussions,
            "success_rate": stats.success_rate,
            "popular_topics": stats.popular_topics
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/admin/broadcast")
async def broadcast_message(
    message: str,
    target_grade: Optional[str] = None,
    target_school: Optional[str] = None
):
    """Broadcast message to students (for announcements)"""
    try:
        users = await db_service.get_users_for_broadcast(target_grade, target_school)
        
        for user in users:
            await whatsapp_service.send_message(user.phone_number, message)
        
        return {"status": "success", "sent_to": len(users)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
