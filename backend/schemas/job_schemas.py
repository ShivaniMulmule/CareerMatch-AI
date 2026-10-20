"""
Job post Pydantic schemas for CareerMatch AI.
Tracks saved target jobs and application pipelines.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class JobCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    company: str = Field(..., min_length=1, max_length=150)
    location: Optional[str] = "Remote"
    job_description: str = Field(..., min_length=20)
    required_experience_years: Optional[float] = 2.0
    status: Optional[str] = "Saved"  # Saved, Applied, Interview, Offer, Rejected


class JobUpdateRequest(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    job_description: Optional[str] = None
    required_experience_years: Optional[float] = None
    status: Optional[str] = None  # Saved, Applied, Interview, Offer, Rejected


class JobResponse(BaseModel):
    id: str
    user_id: str
    title: str
    company: str
    location: str
    job_description: str
    required_experience_years: float
    status: str
    created_at: str
    updated_at: str


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total_count: int
