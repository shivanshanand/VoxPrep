from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime


class RoleType(str, Enum):
    BACKEND = "Backend Developer"
    FRONTEND = "Frontend Developer"
    FULLSTACK = "Full-Stack Developer"
    ML_ENGINEER = "ML Engineer"
    DEVOPS = "DevOps Engineer"
    DATA_SCIENTIST = "Data Scientist"
    MOBILE = "Mobile Developer"


class ExperienceLevel(str, Enum):
    INTERN = "Intern"
    JUNIOR = "Junior (0-2 years)"
    MID = "Mid-level (2-5 years)"
    SENIOR = "Senior (5+ years)"


class FocusArea(str, Enum):
    DSA = "Data Structures & Algorithms"
    SYSTEM_DESIGN = "System Design"
    BEHAVIORAL = "Behavioral"
    DOMAIN_KNOWLEDGE = "Domain Knowledge"


class InterviewPhase(str, Enum):
    INTRODUCTION = "introduction"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CLOSING = "closing"


class InterviewConfig(BaseModel):
    session_id: str
    role: RoleType
    experience: ExperienceLevel
    focus_areas: List[FocusArea] = []
    duration_minutes: int = 30
    candidate_name: Optional[str] = None
    created_at: str = datetime.now().isoformat()


class Question(BaseModel):
    id: str
    text: str
    category: FocusArea
    difficulty: str
    expected_points: List[str]


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    phase: InterviewPhase


class AnswerEvaluation(BaseModel):
    question: str
    answer: str
    score: int  # 1-10
    feedback: str
    strengths: List[str]
    improvements: List[str]
    timestamp: str


class InterviewSession(BaseModel):
    session_id: str
    config: InterviewConfig
    current_phase: InterviewPhase
    questions: List[Question] = []
    current_question_index: int = 0
    messages: List[Message] = []
    evaluations: List[AnswerEvaluation] = []
    start_time: str
    end_time: Optional[str] = None
    overall_score: Optional[float] = None
