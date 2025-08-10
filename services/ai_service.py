import os
import numpy as np
from typing import List, Optional
import logging
from sentence_transformers import SentenceTransformer
import faiss
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    solution: str
    confidence: float
    steps: List[str]
    similar_questions: List[str]

@dataclass
class SimilarQuestion:
    question: str
    answer: str
    source: str  # WAEC or JAMB
    year: int
    similarity_score: float

class AIService:
    def __init__(self):
        # Initialize sentence transformer for question similarity
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize FAISS index for fast similarity search
        self.question_index = None
        self.question_database = []
        
        # Load WAEC/JAMB questions database
        self._load_question_database()
    
    def check_status(self) -> bool:
        """Check if AI service is available"""
        return self.sentence_model is not None
    
    def _load_question_database(self):
        """Load WAEC/JAMB questions and create FAISS index"""
        try:
            # Sample WAEC/JAMB questions (in production, load from database)
            sample_questions = [
                {
                    "question": "Solve for x: 2x + 5 = 13",
                    "answer": "x = 4. Step 1: Subtract 5 from both sides: 2x = 8. Step 2: Divide by 2: x = 4",
                    "source": "WAEC",
                    "year": 2023,
                    "topic": "Linear Equations"
                },
                {
                    "question": "Find the area of a circle with radius 7cm",
                    "answer": "Area = πr² = π × 7² = 49π = 153.94 cm²",
                    "source": "JAMB",
                    "year": 2023,
                    "topic": "Geometry"
                },
                {
                    "question": "Factorize x² - 9",
                    "answer": "x² - 9 = (x + 3)(x - 3) using difference of squares",
                    "source": "WAEC",
                    "year": 2022,
                    "topic": "Algebra"
                }
            ]
            
            self.question_database = sample_questions
            
            # Create embeddings for questions
            question_texts = [q["question"] for q in sample_questions]
            embeddings = self.sentence_model.encode(question_texts)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.question_index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.question_index.add(embeddings.astype('float32'))
            
            logger.info(f"Loaded {len(sample_questions)} questions into FAISS index")
            
        except Exception as e:
            logger.error(f"Failed to load question database: {str(e)}")
    
    def detect_language(self, text: str) -> str:
        """Detect language of the input text"""
        # Simple language detection based on common words
        hausa_words = ['ina', 'yaya', 'wannan', 'da', 'shi', 'ta']
        yoruba_words = ['bawo', 'nibo', 'kini', 'ati', 'ni', 'pe']
        igbo_words = ['kedu', 'gini', 'na', 'nke', 'ya', 'ka']
        
        text_lower = text.lower()
        
        hausa_count = sum(1 for word in hausa_words if word in text_lower)
        yoruba_count = sum(1 for word in yoruba_words if word in text_lower)
        igbo_count = sum(1 for word in igbo_words if word in text_lower)
        
        if hausa_count > 0:
            return "hausa"
        elif yoruba_count > 0:
            return "yoruba"
        elif igbo_count > 0:
            return "igbo"
        else:
            return "english"
    
    async def find_similar_questions(self, question: str, k: int = 3) -> List[SimilarQuestion]:
        """Find similar questions from WAEC/JAMB database"""
        if not self.question_index:
            return []
        
        try:
            # Encode the input question
            query_embedding = self.sentence_model.encode([question])
            faiss.normalize_L2(query_embedding)
            
            # Search for similar questions
            scores, indices = self.question_index.search(query_embedding.astype('float32'), k)
            
            similar_questions = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.question_database):
                    q = self.question_database[idx]
                    similar_questions.append(SimilarQuestion(
                        question=q["question"],
                        answer=q["answer"],
                        source=q["source"],
                        year=q["year"],
                        similarity_score=float(score)
                    ))
            
            return similar_questions
            
        except Exception as e:
            logger.error(f"Error finding similar questions: {str(e)}")
            return []
    
    async def generate_math_solution(
        self, 
        question: str, 
        similar_questions: List[SimilarQuestion],
        language: str = "english",
        grade_level: str = "SS2"
    ) -> AIResponse:
        """Generate AI-powered math solution"""
        try:
            # Analyze question type
            question_type = self._classify_question_type(question)
            
            # Generate solution based on question type
            solution = self._solve_math_problem(question, question_type, similar_questions)
            
            # Translate if needed
            if language != "english":
                solution = self._translate_solution(solution, language)
            
            # Calculate confidence based on question complexity and similarity
            confidence = self._calculate_confidence(question, similar_questions)
            
            # Extract solution steps
            steps = self._extract_solution_steps(solution)
            
            return AIResponse(
                solution=solution,
                confidence=confidence,
                steps=steps,
                similar_questions=[q.question for q in similar_questions[:2]]
            )
            
        except Exception as e:
            logger.error(f"Error generating solution: {str(e)}")
            return AIResponse(
                solution="I'm having trouble solving this problem. Please try rephrasing your question or ask a teacher for help.",
                confidence=0.0,
                steps=[],
                similar_questions=[]
            )
    
    def _classify_question_type(self, question: str) -> str:
        """Classify the type of math question"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['solve', 'find x', 'equation']):
            return "algebra"
        elif any(word in question_lower for word in ['area', 'volume', 'perimeter', 'circle', 'triangle']):
            return "geometry"
        elif any(word in question_lower for word in ['probability', 'chance', 'likely']):
            return "probability"
        elif any(word in question_lower for word in ['derivative', 'integral', 'limit']):
            return "calculus"
        else:
            return "general"
    
    def _solve_math_problem(
        self, 
        question: str, 
        question_type: str, 
        similar_questions: List[SimilarQuestion]
    ) -> str:
        """Generate solution for math problem"""
        
        # Use similar questions as context
        context = ""
        if similar_questions:
            context = f"Similar solved examples:\n"
            for sq in similar_questions[:2]:
                context += f"Q: {sq.question}\nA: {sq.answer}\n\n"
        
        # Generate solution based on question type
        if question_type == "algebra":
            return self._solve_algebra_problem(question, context)
        elif question_type == "geometry":
            return self._solve_geometry_problem(question, context)
        else:
            return self._solve_general_problem(question, context)
    
    def _solve_algebra_problem(self, question: str, context: str) -> str:
        """Solve algebra problems"""
        # Extract equation from question
        equation_match = re.search(r'([0-9x\+\-\*\/\=\s$$$$]+)', question)
        
        if equation_match:
            equation = equation_match.group(1).strip()
            
            # Simple linear equation solver
            if '=' in equation and 'x' in equation:
                try:
                    # Parse simple linear equations like "2x + 5 = 13"
                    left, right = equation.split('=')
                    left, right = left.strip(), right.strip()
                    
                    # This is a simplified solver - in production, use a proper math library
                    solution = f"""
🔢 **Solving: {equation}**

**Step 1:** Isolate the variable term
**Step 2:** Perform arithmetic operations
**Step 3:** Find the value of x

*Note: This is a simplified solution. For complex equations, please provide more details.*

{context}
                    """
                    return solution
                except:
                    pass
        
        return f"I can help you solve this algebra problem! Please provide the equation clearly, for example: '2x + 5 = 13'\n\n{context}"
    
    def _solve_geometry_problem(self, question: str, context: str) -> str:
        """Solve geometry problems"""
        question_lower = question.lower()
        
        if 'area' in question_lower and 'circle' in question_lower:
            return f"""
📐 **Circle Area Problem**

**Formula:** Area = πr²

**Steps:**
1. Identify the radius (r)
2. Square the radius (r²)
3. Multiply by π (3.14159...)

**Example:** If radius = 7cm
Area = π × 7² = π × 49 = 153.94 cm²

{context}
            """
        
        elif 'area' in question_lower and 'triangle' in question_lower:
            return f"""
📐 **Triangle Area Problem**

**Formula:** Area = ½ × base × height

**Steps:**
1. Identify the base and height
2. Multiply base × height
3. Divide by 2

{context}
            """
        
        return f"I can help with geometry! Please specify what you need to find (area, volume, perimeter, etc.) and provide the measurements.\n\n{context}"
    
    def _solve_general_problem(self, question: str, context: str) -> str:
        """Solve general math problems"""
        return f"""
📚 **Math Problem Solution**

I understand you need help with: "{question}"

**Approach:**
1. Identify what is given
2. Determine what needs to be found
3. Choose the appropriate formula or method
4. Solve step by step

Please provide more specific details about the problem, including any numbers or measurements involved.

{context}
        """
    
    def _translate_solution(self, solution: str, target_language: str) -> str:
        """Translate solution to local language"""
        # Simple translation mapping (in production, use proper translation service)
        translations = {
            "hausa": {
                "Step": "Mataki",
                "Solution": "Mafita",
                "Formula": "Dabara",
                "Answer": "Amsa"
            },
            "yoruba": {
                "Step": "Igbesẹ",
                "Solution": "Ojutu",
                "Formula": "Agbekalẹ",
                "Answer": "Idahun"
            },
            "igbo": {
                "Step": "Nzọụkwụ",
                "Solution": "Azịza",
                "Formula": "Usoro",
                "Answer": "Azịza"
            }
        }
        
        if target_language in translations:
            for english, local in translations[target_language].items():
                solution = solution.replace(english, local)
        
        return solution
    
    def _calculate_confidence(self, question: str, similar_questions: List[SimilarQuestion]) -> float:
        """Calculate confidence score for the solution"""
        base_confidence = 0.5
        
        # Increase confidence if we have similar questions
        if similar_questions:
            avg_similarity = sum(q.similarity_score for q in similar_questions) / len(similar_questions)
            base_confidence += avg_similarity * 0.3
        
        # Increase confidence for common question types
        if any(word in question.lower() for word in ['solve', 'find', 'calculate']):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _extract_solution_steps(self, solution: str) -> List[str]:
        """Extract solution steps from the generated solution"""
        steps = []
        lines = solution.split('\n')
        
        for line in lines:
            if 'step' in line.lower() or line.strip().startswith(('1.', '2.', '3.')):
                steps.append(line.strip())
        
        return steps
