from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

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

class RateLimitDB(Base):
    __tablename__ = "rate_limits"
    
    ip_address = Column(String, primary_key=True, index=True)
    usage_count = Column(Integer, default=0)
    reset_time = Column(DateTime)

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

async def get_rate_limit(ip_address: str):
    async with async_session() as db:
        result = await db.get(RateLimitDB, ip_address)
        return result

async def save_rate_limit(rate_limit_data: dict):
    async with async_session() as db:
        rate_limit = await db.get(RateLimitDB, rate_limit_data["ip_address"])
        if rate_limit:
            for key, value in rate_limit_data.items():
                setattr(rate_limit, key, value)
        else:
            rate_limit = RateLimitDB(**rate_limit_data)
            db.add(rate_limit)
        await db.commit()
