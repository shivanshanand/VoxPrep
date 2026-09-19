from datetime import datetime, timedelta

from fastapi import APIRouter, Request

from app.database import get_rate_limit
from app.models.interview import ExperienceLevel, RoleType

router = APIRouter()

@router.get("/roles")
async def get_roles():
    """Get available interview roles"""
    return {
        "roles": [{"value": role.name, "label": role.value} for role in RoleType]
    }

@router.get("/experience-levels")
async def get_experience_levels():
    """Get available experience levels"""
    return {
        "levels": [{"value": level.name, "label": level.value} for level in ExperienceLevel]
    }

@router.get("/rate-limit")
async def get_user_rate_limit(request: Request):
    """Get the current rate limit for the user based on IP"""
    client_ip = request.client.host if request.client else "unknown"
    rate_limit = await get_rate_limit(client_ip)
    
    now = datetime.now()
    if rate_limit:
        if now > rate_limit.reset_time:
            return {"usage_count": 0, "max_usage": 3, "reset_time": (now + timedelta(days=3)).isoformat()}
        return {"usage_count": rate_limit.usage_count, "max_usage": 3, "reset_time": rate_limit.reset_time.isoformat()}
    else:
        return {"usage_count": 0, "max_usage": 3, "reset_time": (now + timedelta(days=3)).isoformat()}
