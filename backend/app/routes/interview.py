from fastapi import APIRouter
from app.models.interview import RoleType, ExperienceLevel
from typing import List

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
