"""
Resume Pydantic schemas for CareerMatch AI.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class ResumeResponse(BaseModel):
    id: str
    user_id: str
    original_filename: str
    stored_filename: str
    file_size_bytes: int
    char_count: int
    word_count: int
    detected_role: Optional[str] = "Candidate"
    experience_summary: Optional[Dict[str, Any]] = None
    education_summary: Optional[Dict[str, Any]] = None
    extracted_text_preview: str
    storage_provider: str
    download_url: str
    created_at: str
    is_active: bool = True


class ResumeListResponse(BaseModel):
    resumes: List[ResumeResponse]
    total_count: int
