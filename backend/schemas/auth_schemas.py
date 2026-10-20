"""
Authentication Pydantic schemas for CareerMatch AI.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    target_role: Optional[str] = "Machine Learning Engineer"
    experience_level: Optional[str] = "Fresher"


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    target_role: str
    experience_level: str
    created_at: str


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
