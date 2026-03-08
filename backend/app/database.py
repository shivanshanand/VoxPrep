from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Text, Float, Integer, JSON, DateTime
from datetime import datetime

# Database URL
DATABASE_URL = "sqlite+aiosqlite:///./interviews.db"

# Create engine
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Models
class InterviewSessionDB(Base):
    __tablename__ = "interview_sessions"
    
    session_id = Column(String, primary_key=True, index=True)
    role = Column(String)
    experience = Column(String)
    candidate_name = Column(String, nullable=True)
    current_phase = Column(String)
    messages = Column(JSON)  # Store as JSON
    evaluations = Column(JSON)  # Store as JSON
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    overall_score = Column(Float, nullable=True)

# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Database operations
async def save_session(session_data: dict):
    async with async_session() as db:
        session = InterviewSessionDB(**session_data)
        db.add(session)
        await db.commit()

async def get_session(session_id: str):
    async with async_session() as db:
        result = await db.get(InterviewSessionDB, session_id)
        return result

async def update_session(session_id: str, updates: dict):
    async with async_session() as db:
        session = await db.get(InterviewSessionDB, session_id)
        if session:
            for key, value in updates.items():
                setattr(session, key, value)
            await db.commit()
