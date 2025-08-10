import os
import asyncpg
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from models.schemas import UserProfile, Question, Response, PeerDiscussion

logger = logging.getLogger(__name__)

@dataclass
class PlatformStats:
    total_users: int
    questions_today: int
    active_discussions: int
    success_rate: float
    popular_topics: List[Dict[str, Any]]

class DatabaseService:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool = None
    
    async def init_pool(self):
        """Initialize database connection pool"""
        if not self.database_url:
            logger.error("DATABASE_URL not found")
            return
        
        try:
            self.pool = await asyncpg.create_pool(self.database_url)
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {str(e)}")
    
    async def check_connection(self) -> bool:
        """Check database connection"""
        if not self.pool:
            await self.init_pool()
        
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {str(e)}")
            return False
    
    async def get_or_create_user(self, phone_number: str) -> UserProfile:
        """Get existing user or create new one"""
        if not self.pool:
            await self.init_pool()
        
        try:
            async with self.pool.acquire() as conn:
                # Check if user exists
                user_record = await conn.fetchrow(
                    "SELECT * FROM users WHERE phone_number = $1",
                    phone_number
                )
                
                if user_record:
                    return UserProfile(
                        id=user_record['id'],
                        phone_number=user_record['phone_number'],
                        name=user_record['name'],
                        school=user_record['school'],
                        grade_level=user_record['grade_level'],
                        preferred_language=user_record['preferred_language'],
                        created_at=user_record['created_at']
                    )
                else:
                    # Create new user
                    user_id = await conn.fetchval(
                        """
                        INSERT INTO users (phone_number, name, grade_level, preferred_language, created_at)
                        VALUES ($1, $2, $3, $4, $5)
                        RETURNING id
                        """,
                        phone_number,
                        "New Student",  # Default name
                        "SS2",  # Default grade
                        "english",  # Default language
                        datetime.utcnow()
                    )
                    
                    return UserProfile(
                        id=user_id,
                        phone_number=phone_number,
                        name="New Student",
                        school=None,
                        grade_level="SS2",
                        preferred_language="english",
                        created_at=datetime.utcnow()
                    )
        
        except Exception as e:
            logger.error(f"Error getting/creating user: {str(e)}")
            # Return a default user profile if database fails
            return UserProfile(
                id=0,
                phone_number=phone_number,
                name="Guest User",
                school=None,
                grade_level="SS2",
                preferred_language="english",
                created_at=datetime.utcnow()
            )
    
    async def save_question(
        self, 
        user_id: int, 
        question_text: str, 
        question_type: str,
        language: str
    ) -> Question:
        """Save user question to database"""
        if not self.pool:
            await self.init_pool()
        
        try:
            async with self.pool.acquire() as conn:
                question_id = await conn.fetchval(
                    """
                    INSERT INTO questions (user_id, question_text, question_type, language, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                    """,
                    user_id,
                    question_text,
                    question_type,
                    language,
                    datetime.utcnow()
                )
                
                return Question(
                    id=question_id,
                    user_id=user_id,
                    question_text=question_text,
                    question_type=question_type,
                    language=language,
                    created_at=datetime.utcnow()
                )
        
        except Exception as e:
            logger.error(f"Error saving question: {str(e)}")
            # Return a mock question if database fails
            return Question(
                id=0,
                user_id=user_id,
                question_text=question_text,
                question_type=question_type,
                language=language,
                created_at=datetime.utcnow()
            )
    
    async def save_response(
        self, 
        question_id: int, 
        response_text: str, 
        confidence_score: float
    ) -> Response:
        """Save AI response to database"""
        if not self.pool:
            await self.init_pool()
        
        try:
            async with self.pool.acquire() as conn:
                response_id = await conn.fetchval(
                    """
                    INSERT INTO responses (question_id, response_text, confidence_score, created_at)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                    """,
                    question_id,
                    response_text,
                    confidence_score,
                    datetime.utcnow()
                )
                
                return Response(
                    id=response_id,
                    question_id=question_id,
                    response_text=response_text,
                    confidence_score=confidence_score,
                    created_at=datetime.utcnow()
                )
        
        except Exception as e:
            logger.error(f"Error saving response: {str(e)}")
            return Response(
                id=0,
                question_id=question_id,
                response_text=response_text,
                confidence_score=confidence_score,
                created_at=datetime.utcnow()
            )
    
    async def get_user_questions(self, user_id: int, limit: int = 10) -> List[Question]:
        """Get user's question history"""
        if not self.pool:
            await self.init_pool()
        
        try:
            async with self.pool.acquire() as conn:
                records = await conn.fetch(
                    """
                    SELECT * FROM questions 
                    WHERE user_id = $1 
                    ORDER BY created_at DESC 
                    LIMIT $2
                    """,
                    user_id,
                    limit
                )
                
                return [
                    Question(
                        id=record['id'],
                        user_id=record['user_id'],
                        question_text=record['question_text'],
                        question_type=record['question_type'],
                        language=record['language'],
                        created_at=record['created_at']
                    )
                    for record in records
                ]
        
        except Exception as e:
            logger.error(f"Error getting user questions: {str(e)}")
            return []
    
    async def get_platform_stats(self) -> PlatformStats:
        """Get platform analytics"""
        if not self.pool:
            await self.init_pool()
        
        try:
            async with self.pool.acquire() as conn:
                # Get total users
                total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
                
                # Get questions today
                today = datetime.utcnow().date()
                questions_today = await conn.fetchval(
                    "SELECT COUNT(*) FROM questions WHERE DATE(created_at) = $1",
                    today
                )
                
                # Get active discussions (mock for now)
                active_discussions = 5
                
                # Calculate success rate (mock for now)
                success_rate = 0.85
                
                # Get popular topics (mock for now)
                popular_topics = [
                    {"topic": "Algebra", "count": 45},
                    {"topic": "Geometry", "count": 32},
                    {"topic": "Calculus", "count": 28}
                ]
                
                return PlatformStats(
                    total_users=total_users or 0,
                    questions_today=questions_today or 0,
                    active_discussions=active_discussions,
                    success_rate=success_rate,
                    popular_topics=popular_topics
                )
        
        except Exception as e:
            logger.error(f"Error getting platform stats: {str(e)}")
            return PlatformStats(
                total_users=0,
                questions_today=0,
                active_discussions=0,
                success_rate=0.0,
                popular_topics=[]
            )
