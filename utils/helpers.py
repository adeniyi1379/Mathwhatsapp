import re
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def clean_phone_number(phone_number: str) -> str:
    """Clean and format phone number for Nigerian numbers"""
    # Remove all non-digit characters
    clean_number = re.sub(r'[^\d]', '', phone_number)
    
    # Handle Nigerian number formats
    if clean_number.startswith('234'):
        return f"+{clean_number}"
    elif clean_number.startswith('0'):
        return f"+234{clean_number[1:]}"
    elif len(clean_number) == 10:
        return f"+234{clean_number}"
    else:
        return f"+{clean_number}"

def extract_math_expressions(text: str) -> List[str]:
    """Extract mathematical expressions from text"""
    # Common math patterns
    patterns = [
        r'[0-9x\+\-\*\/\=$$$$\^\s]+=[0-9x\+\-\*\/$$$$\^\s]+',  # Equations
        r'[0-9]+\s*[\+\-\*\/]\s*[0-9x]+',  # Simple expressions
        r'[0-9]*x[\+\-][0-9]+\s*=\s*[0-9]+',  # Linear equations
        r'x\^?[0-9]*[\+\-][0-9x\^]*\s*=\s*[0-9]+',  # Quadratic equations
    ]
    
    expressions = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        expressions.extend(matches)
    
    return list(set(expressions))  # Remove duplicates

def classify_math_topic(question: str) -> str:
    """Classify the mathematical topic of a question"""
    question_lower = question.lower()
    
    # Topic keywords mapping
    topic_keywords = {
        'algebra': ['solve', 'equation', 'variable', 'x =', 'find x', 'linear', 'quadratic'],
        'geometry': ['area', 'volume', 'perimeter', 'circle', 'triangle', 'rectangle', 'square', 'angle'],
        'trigonometry': ['sin', 'cos', 'tan', 'sine', 'cosine', 'tangent', 'angle', 'triangle'],
        'calculus': ['derivative', 'integral', 'limit', 'differentiate', 'integrate'],
        'statistics': ['mean', 'median', 'mode', 'average', 'probability', 'standard deviation'],
        'logarithms': ['log', 'logarithm', 'ln', 'exponential'],
        'indices': ['power', 'exponent', 'index', 'square', 'cube'],
        'fractions': ['fraction', 'numerator', 'denominator', '/', 'half', 'quarter'],
        'surds': ['square root', 'surd', '√', 'radical'],
        'coordinate_geometry': ['coordinate', 'graph', 'plot', 'x-axis', 'y-axis', 'gradient', 'slope']
    }
    
    # Count keyword matches for each topic
    topic_scores = {}
    for topic, keywords in topic_keywords.items():
        score = sum(1 for keyword in keywords if keyword in question_lower)
        if score > 0:
            topic_scores[topic] = score
    
    # Return topic with highest score, or 'general' if no matches
    if topic_scores:
        return max(topic_scores, key=topic_scores.get)
    else:
        return 'general'

def estimate_difficulty(question: str) -> str:
    """Estimate the difficulty level of a math question"""
    question_lower = question.lower()
    
    # Difficulty indicators
    easy_indicators = ['add', 'subtract', 'multiply', 'divide', 'simple', 'basic']
    medium_indicators = ['solve', 'find', 'calculate', 'equation', 'formula']
    hard_indicators = ['prove', 'derive', 'complex', 'advanced', 'integral', 'derivative']
    
    easy_score = sum(1 for indicator in easy_indicators if indicator in question_lower)
    medium_score = sum(1 for indicator in medium_indicators if indicator in question_lower)
    hard_score = sum(1 for indicator in hard_indicators if indicator in question_lower)
    
    if hard_score > 0:
        return 'hard'
    elif medium_score > easy_score:
        return 'medium'
    else:
        return 'easy'

def generate_question_hash(question_text: str) -> str:
    """Generate a hash for question deduplication"""
    # Normalize the question text
    normalized = re.sub(r'\s+', ' ', question_text.lower().strip())
    normalized = re.sub(r'[^\w\s\+\-\*\/\=$$$$]', '', normalized)
    
    # Generate hash
    return hashlib.md5(normalized.encode()).hexdigest()

def format_solution_steps(solution: str) -> List[str]:
    """Format solution into clear steps"""
    # Split by common step indicators
    step_patterns = [
        r'step\s*\d+:?',
        r'\d+\.',
        r'first,?',
        r'second,?',
        r'then,?',
        r'next,?',
        r'finally,?'
    ]
    
    steps = []
    current_step = ""
    
    for line in solution.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Check if line starts with a step indicator
        is_new_step = any(re.match(pattern, line.lower()) for pattern in step_patterns)
        
        if is_new_step and current_step:
            steps.append(current_step.strip())
            current_step = line
        else:
            current_step += " " + line if current_step else line
    
    if current_step:
        steps.append(current_step.strip())
    
    return steps

def calculate_engagement_score(
    questions_asked: int,
    days_active: int,
    success_rate: float,
    peer_interactions: int
) -> float:
    """Calculate student engagement score"""
    # Normalize factors
    question_score = min(questions_asked / 10, 1.0)  # Max at 10 questions
    activity_score = min(days_active / 7, 1.0)  # Max at 7 days
    success_score = success_rate
    interaction_score = min(peer_interactions / 5, 1.0)  # Max at 5 interactions
    
    # Weighted average
    engagement = (
        question_score * 0.3 +
        activity_score * 0.2 +
        success_score * 0.3 +
        interaction_score * 0.2
    )
    
    return round(engagement, 2)

def get_nigerian_time() -> datetime:
    """Get current time in Nigerian timezone (WAT)"""
    from datetime import timezone, timedelta
    
    # Nigeria is UTC+1
    nigerian_tz = timezone(timedelta(hours=1))
    return datetime.now(nigerian_tz)

def is_school_hours() -> bool:
    """Check if current time is during school hours in Nigeria"""
    current_time = get_nigerian_time().time()
    
    # School hours: 8 AM to 4 PM, Monday to Friday
    school_start = datetime.strptime("08:00", "%H:%M").time()
    school_end = datetime.strptime("16:00", "%H:%M").time()
    
    current_day = get_nigerian_time().weekday()  # 0 = Monday, 6 = Sunday
    
    return (
        current_day < 5 and  # Monday to Friday
        school_start <= current_time <= school_end
    )

def create_whatsapp_link(phone_number: str, message: str = "") -> str:
    """Create WhatsApp link for easy sharing"""
    clean_number = clean_phone_number(phone_number).replace("+", "")
    encoded_message = message.replace(" ", "%20").replace("\n", "%0A")
    
    return f"https://wa.me/{clean_number}?text={encoded_message}"
