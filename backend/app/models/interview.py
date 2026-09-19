from datetime import datetime
from enum import Enum

from pydantic import BaseModel


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
    focus_areas: list[FocusArea] = []
    duration_minutes: int = 30
    candidate_name: str | None = None
    created_at: str = datetime.now().isoformat()


class Question(BaseModel):
    id: str
    text: str
    category: FocusArea
    difficulty: str
    expected_points: list[str]


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
    strengths: list[str]
    improvements: list[str]
    timestamp: str


class InterviewSession(BaseModel):
    session_id: str
    config: InterviewConfig
    current_phase: InterviewPhase
    questions: list[Question] = []
    current_question_index: int = 0
    messages: list[Message] = []
    evaluations: list[AnswerEvaluation] = []
    start_time: str
    end_time: str | None = None
    overall_score: float | None = None
