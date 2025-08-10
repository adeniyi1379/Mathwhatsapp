from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WebhookMessage(BaseModel):
    from_number: str
    message_type: str  # text, image, voice
    text: Optional[str] = None
    media_url: Optional[str] = None
    timestamp: datetime

class UserProfile(BaseModel):
    id: Optional[int] = None
    phone_number: str
    name: Optional[str] = None
    school: Optional[str] = None
    grade_level: str = "SS2"  # SS1, SS2, SS3
    preferred_language: str = "english"
    created_at: Optional[datetime] = None

class Question(BaseModel):
    id: Optional[int] = None
    user_id: int
    question_text: str
    question_type: str  # text, image, voice
    language: str
    created_at: Optional[datetime] = None

class Response(BaseModel):
    id: Optional[int] = None
    question_id: int
    response_text: str
    confidence_score: float
    created_at: Optional[datetime] = None

class PeerDiscussion(BaseModel):
    id: Optional[int] = None
    question_id: int
    participants: List[UserProfile]
    question_preview: str
    status: str = "active"  # active, closed
    created_at: Optional[datetime] = None
