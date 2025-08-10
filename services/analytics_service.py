import os
import httpx
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class StudentAnalytics:
    user_id: int
    name: str
    questions_asked: int
    topics_covered: List[str]
    success_rate: float
    engagement_score: float
    last_active: datetime

@dataclass
class SchoolAnalytics:
    school_id: int
    school_name: str
    total_students: int
    active_students: int
    questions_this_week: int
    top_topics: List[Dict[str, Any]]
    average_success_rate: float

@dataclass
class PlatformAnalytics:
    total_users: int
    daily_active_users: int
    questions_today: int
    questions_this_week: int
    success_rate: float
    popular_topics: List[Dict[str, Any]]
    language_distribution: Dict[str, int]
    grade_distribution: Dict[str, int]

class AnalyticsService:
    def __init__(self, db_service):
        self.db_service = db_service
        self.retool_webhook_url = os.getenv("RETOOL_WEBHOOK_URL")
        
    async def get_student_analytics(self, user_id: int) -> Optional[StudentAnalytics]:
        """Get comprehensive analytics for a specific student"""
        try:
            if not self.db_service.pool:
                await self.db_service.init_pool()
            
            async with self.db_service.pool.acquire() as conn:
                # Get user info
                user_info = await conn.fetchrow(
                    "SELECT name, created_at FROM users WHERE id = $1",
                    user_id
                )
                
                if not user_info:
                    return None
                
                # Get question statistics
                week_ago = datetime.utcnow() - timedelta(days=7)
                
                questions_asked = await conn.fetchval(
                    "SELECT COUNT(*) FROM questions WHERE user_id = $1 AND created_at >= $2",
                    user_id, week_ago
                )
                
                # Get topics covered
                topics_result = await conn.fetch(
                    """
                    SELECT topic, COUNT(*) as count 
                    FROM questions 
                    WHERE user_id = $1 AND created_at >= $2 AND topic IS NOT NULL
                    GROUP BY topic 
                    ORDER BY count DESC
                    """,
                    user_id, week_ago
                )
                
                topics_covered = [row['topic'] for row in topics_result]
                
                # Calculate success rate (based on response confidence)
                success_rate_result = await conn.fetchval(
                    """
                    SELECT AVG(r.confidence_score) 
                    FROM responses r 
                    JOIN questions q ON r.question_id = q.id 
                    WHERE q.user_id = $1 AND q.created_at >= $2
                    """,
                    user_id, week_ago
                )
                
                success_rate = float(success_rate_result or 0.0)
                
                # Calculate engagement score
                engagement_score = min(questions_asked * 0.1 + success_rate * 0.5, 1.0)
                
                # Get last activity
                last_active = await conn.fetchval(
                    "SELECT MAX(created_at) FROM questions WHERE user_id = $1",
                    user_id
                )
                
                return StudentAnalytics(
                    user_id=user_id,
                    name=user_info['name'],
                    questions_asked=questions_asked or 0,
                    topics_covered=topics_covered,
                    success_rate=success_rate,
                    engagement_score=engagement_score,
                    last_active=last_active or user_info['created_at']
                )
        
        except Exception as e:
            logger.error(f"Error getting student analytics: {str(e)}")
            return None
    
    async def get_school_analytics(self, school_id: int) -> Optional[SchoolAnalytics]:
        """Get analytics for a specific school"""
        try:
            if not self.db_service.pool:
                await self.db_service.init_pool()
            
            async with self.db_service.pool.acquire() as conn:
                # Get school info
                school_info = await conn.fetchrow(
                    "SELECT name FROM schools WHERE id = $1",
                    school_id
                )
                
                if not school_info:
                    return None
                
                week_ago = datetime.utcnow() - timedelta(days=7)
                
                # Get student counts
                total_students = await conn.fetchval(
                    "SELECT COUNT(*) FROM users WHERE school = $1",
                    school_info['name']
                )
                
                active_students = await conn.fetchval(
                    """
                    SELECT COUNT(DISTINCT u.id) 
                    FROM users u 
                    JOIN questions q ON u.id = q.user_id 
                    WHERE u.school = $1 AND q.created_at >= $2
                    """,
                    school_info['name'], week_ago
                )
                
                # Get questions this week
                questions_this_week = await conn.fetchval(
                    """
                    SELECT COUNT(*) 
                    FROM questions q 
                    JOIN users u ON q.user_id = u.id 
                    WHERE u.school = $1 AND q.created_at >= $2
                    """,
                    school_info['name'], week_ago
                )
                
                # Get top topics
                top_topics_result = await conn.fetch(
                    """
                    SELECT q.topic, COUNT(*) as count 
                    FROM questions q 
                    JOIN users u ON q.user_id = u.id 
                    WHERE u.school = $1 AND q.created_at >= $2 AND q.topic IS NOT NULL
                    GROUP BY q.topic 
                    ORDER BY count DESC 
                    LIMIT 5
                    """,
                    school_info['name'], week_ago
                )
                
                top_topics = [
                    {"topic": row['topic'], "count": row['count']} 
                    for row in top_topics_result
                ]
                
                # Calculate average success rate
                avg_success_rate = await conn.fetchval(
                    """
                    SELECT AVG(r.confidence_score) 
                    FROM responses r 
                    JOIN questions q ON r.question_id = q.id 
                    JOIN users u ON q.user_id = u.id 
                    WHERE u.school = $1 AND q.created_at >= $2
                    """,
                    school_info['name'], week_ago
                )
                
                return SchoolAnalytics(
                    school_id=school_id,
                    school_name=school_info['name'],
                    total_students=total_students or 0,
                    active_students=active_students or 0,
                    questions_this_week=questions_this_week or 0,
                    top_topics=top_topics,
                    average_success_rate=float(avg_success_rate or 0.0)
                )
        
        except Exception as e:
            logger.error(f"Error getting school analytics: {str(e)}")
            return None
    
    async def get_platform_analytics(self) -> PlatformAnalytics:
        """Get comprehensive platform analytics"""
        try:
            if not self.db_service.pool:
                await self.db_service.init_pool()
            
            async with self.db_service.pool.acquire() as conn:
                today = datetime.utcnow().date()
                week_ago = datetime.utcnow() - timedelta(days=7)
                
                # Total users
                total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
                
                # Daily active users
                daily_active_users = await conn.fetchval(
                    """
                    SELECT COUNT(DISTINCT user_id) 
                    FROM questions 
                    WHERE DATE(created_at) = $1
                    """,
                    today
                )
                
                # Questions today
                questions_today = await conn.fetchval(
                    "SELECT COUNT(*) FROM questions WHERE DATE(created_at) = $1",
                    today
                )
                
                # Questions this week
                questions_this_week = await conn.fetchval(
                    "SELECT COUNT(*) FROM questions WHERE created_at >= $1",
                    week_ago
                )
                
                # Success rate
                success_rate = await conn.fetchval(
                    """
                    SELECT AVG(confidence_score) 
                    FROM responses r 
                    JOIN questions q ON r.question_id = q.id 
                    WHERE q.created_at >= $1
                    """,
                    week_ago
                )
                
                # Popular topics
                popular_topics_result = await conn.fetch(
                    """
                    SELECT topic, COUNT(*) as count 
                    FROM questions 
                    WHERE created_at >= $1 AND topic IS NOT NULL
                    GROUP BY topic 
                    ORDER BY count DESC 
                    LIMIT 10
                    """,
                    week_ago
                )
                
                popular_topics = [
                    {"topic": row['topic'], "count": row['count']} 
                    for row in popular_topics_result
                ]
                
                # Language distribution
                language_dist_result = await conn.fetch(
                    """
                    SELECT language, COUNT(*) as count 
                    FROM questions 
                    WHERE created_at >= $1 
                    GROUP BY language
                    """,
                    week_ago
                )
                
                language_distribution = {
                    row['language']: row['count'] 
                    for row in language_dist_result
                }
                
                # Grade distribution
                grade_dist_result = await conn.fetch(
                    """
                    SELECT u.grade_level, COUNT(DISTINCT u.id) as count 
                    FROM users u 
                    JOIN questions q ON u.id = q.user_id 
                    WHERE q.created_at >= $1 
                    GROUP BY u.grade_level
                    """,
                    week_ago
                )
                
                grade_distribution = {
                    row['grade_level']: row['count'] 
                    for row in grade_dist_result
                }
                
                return PlatformAnalytics(
                    total_users=total_users or 0,
                    daily_active_users=daily_active_users or 0,
                    questions_today=questions_today or 0,
                    questions_this_week=questions_this_week or 0,
                    success_rate=float(success_rate or 0.0),
                    popular_topics=popular_topics,
                    language_distribution=language_distribution,
                    grade_distribution=grade_distribution
                )
        
        except Exception as e:
            logger.error(f"Error getting platform analytics: {str(e)}")
            return PlatformAnalytics(
                total_users=0,
                daily_active_users=0,
                questions_today=0,
                questions_this_week=0,
                success_rate=0.0,
                popular_topics=[],
                language_distribution={},
                grade_distribution={}
            )
    
    async def send_analytics_to_retool(self, analytics_data: Dict[str, Any]) -> bool:
        """Send analytics data to Retool dashboard"""
        if not self.retool_webhook_url:
            logger.warning("Retool webhook URL not configured")
            return False
        
        try:
            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "data": analytics_data
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.retool_webhook_url,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info("Analytics data sent to Retool successfully")
                    return True
                else:
                    logger.error(f"Failed to send analytics to Retool: {response.status_code}")
                    return False
        
        except Exception as e:
            logger.error(f"Error sending analytics to Retool: {str(e)}")
            return False
    
    async def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily analytics report"""
        platform_analytics = await self.get_platform_analytics()
        
        report = {
            "date": datetime.utcnow().date().isoformat(),
            "platform_metrics": {
                "total_users": platform_analytics.total_users,
                "daily_active_users": platform_analytics.daily_active_users,
                "questions_today": platform_analytics.questions_today,
                "success_rate": platform_analytics.success_rate
            },
            "engagement_metrics": {
                "popular_topics": platform_analytics.popular_topics[:5],
                "language_distribution": platform_analytics.language_distribution,
                "grade_distribution": platform_analytics.grade_distribution
            }
        }
        
        # Send to Retool
        await self.send_analytics_to_retool(report)
        
        return report
