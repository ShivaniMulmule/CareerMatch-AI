"""
Authentication API Endpoints for CareerMatch AI.
Registers users, verifies credentials, and issues JWT access tokens.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict

from backend.schemas.auth_schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse
)
from backend.dependencies.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from database.db_client import get_database


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(req: UserRegisterRequest, db: Any = Depends(get_database)):
    users_col = db.get_collection("users") if hasattr(db, "get_collection") else db["users"]
    
    # Check if user already exists
    existing_user = await users_col.find_one({"email": req.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    user_doc = {
        "email": req.email.lower(),
        "password_hash": hash_password(req.password),
        "full_name": req.full_name.strip(),
        "target_role": req.target_role or "Machine Learning Engineer",
        "experience_level": req.experience_level or "Fresher",
        "created_at": datetime.now().isoformat()
    }

    insert_result = await users_col.insert_one(user_doc)
    user_id = str(insert_result.inserted_id)

    token = create_access_token(data={"sub": user_id, "email": user_doc["email"]})

    user_response = UserResponse(
        id=user_id,
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        target_role=user_doc["target_role"],
        experience_level=user_doc["experience_level"],
        created_at=user_doc["created_at"]
    )

    return TokenResponse(access_token=token, token_type="bearer", user=user_response)


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLoginRequest, db: Any = Depends(get_database)):
    users_col = db.get_collection("users") if hasattr(db, "get_collection") else db["users"]
    
    user = await users_col.find_one({"email": req.email.lower()})
    if not user or not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    user_id = str(user.get("_id"))
    token = create_access_token(data={"sub": user_id, "email": user["email"]})

    user_response = UserResponse(
        id=user_id,
        email=user["email"],
        full_name=user.get("full_name", "User"),
        target_role=user.get("target_role", "Machine Learning Engineer"),
        experience_level=user.get("experience_level", "Fresher"),
        created_at=user.get("created_at", datetime.now().isoformat())
    )

    return TokenResponse(access_token=token, token_type="bearer", user=user_response)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.get("_id")),
        email=current_user["email"],
        full_name=current_user.get("full_name", "User"),
        target_role=current_user.get("target_role", "Machine Learning Engineer"),
        experience_level=current_user.get("experience_level", "Fresher"),
        created_at=current_user.get("created_at", datetime.now().isoformat())
    )
