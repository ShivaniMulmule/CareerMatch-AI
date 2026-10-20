"""
Profile Management Endpoints for CareerMatch AI.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict

from backend.schemas.auth_schemas import UserResponse, ProfileUpdateRequest
from backend.dependencies.auth import get_current_user
from database.db_client import get_database


router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("", response_model=UserResponse)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.get("_id")),
        email=current_user["email"],
        full_name=current_user.get("full_name", "User"),
        target_role=current_user.get("target_role", "Machine Learning Engineer"),
        experience_level=current_user.get("experience_level", "Fresher"),
        created_at=current_user.get("created_at", "")
    )


@router.put("", response_model=UserResponse)
async def update_profile(
    req: ProfileUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    users_col = db.get_collection("users") if hasattr(db, "get_collection") else db["users"]

    updates = {}
    if req.full_name is not None:
        updates["full_name"] = req.full_name.strip()
    if req.target_role is not None:
        updates["target_role"] = req.target_role.strip()
    if req.experience_level is not None:
        updates["experience_level"] = req.experience_level.strip()

    if updates:
        await users_col.update_one({"_id": user_id}, {"$set": updates})

    updated_user = await users_col.find_one({"_id": user_id})
    return UserResponse(
        id=user_id,
        email=updated_user["email"],
        full_name=updated_user.get("full_name", "User"),
        target_role=updated_user.get("target_role", "Machine Learning Engineer"),
        experience_level=updated_user.get("experience_level", "Fresher"),
        created_at=updated_user.get("created_at", "")
    )
