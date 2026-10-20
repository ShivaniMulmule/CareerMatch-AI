"""
Job Tracking and Management Endpoints for CareerMatch AI.
Manages target job postings, updates, and application pipeline statuses.
"""

from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from backend.schemas.job_schemas import JobCreateRequest, JobUpdateRequest, JobResponse, JobListResponse
from backend.dependencies.auth import get_current_user
from database.db_client import get_database


router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.post("", response_model=JobResponse)
async def create_job(
    req: JobCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    jobs_col = db.get_collection("jobs") if hasattr(db, "get_collection") else db["jobs"]

    doc = {
        "user_id": user_id,
        "title": req.title.strip(),
        "company": req.company.strip(),
        "location": req.location or "Remote",
        "job_description": req.job_description.strip(),
        "required_experience_years": float(req.required_experience_years or 2.0),
        "status": req.status or "Saved",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    insert_res = await jobs_col.insert_one(doc)
    doc_id = str(insert_res.inserted_id)

    return JobResponse(
        id=doc_id,
        user_id=user_id,
        title=doc["title"],
        company=doc["company"],
        location=doc["location"],
        job_description=doc["job_description"],
        required_experience_years=doc["required_experience_years"],
        status=doc["status"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"]
    )


@router.get("", response_model=JobListResponse)
async def list_jobs(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    jobs_col = db.get_collection("jobs") if hasattr(db, "get_collection") else db["jobs"]

    records = await jobs_col.find({"user_id": user_id}, sort=[("created_at", -1)])
    results = [
        JobResponse(
            id=str(r.get("_id")),
            user_id=user_id,
            title=r.get("title", "Role"),
            company=r.get("company", "Company"),
            location=r.get("location", "Remote"),
            job_description=r.get("job_description", ""),
            required_experience_years=float(r.get("required_experience_years", 2.0)),
            status=r.get("status", "Saved"),
            created_at=r.get("created_at", datetime.now().isoformat()),
            updated_at=r.get("updated_at", datetime.now().isoformat())
        )
        for r in records
    ]

    return JobListResponse(jobs=results, total_count=len(results))


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    jobs_col = db.get_collection("jobs") if hasattr(db, "get_collection") else db["jobs"]

    r = await jobs_col.find_one({"_id": job_id, "user_id": user_id})
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")

    return JobResponse(
        id=str(r.get("_id")),
        user_id=user_id,
        title=r.get("title", "Role"),
        company=r.get("company", "Company"),
        location=r.get("location", "Remote"),
        job_description=r.get("job_description", ""),
        required_experience_years=float(r.get("required_experience_years", 2.0)),
        status=r.get("status", "Saved"),
        created_at=r.get("created_at", datetime.now().isoformat()),
        updated_at=r.get("updated_at", datetime.now().isoformat())
    )


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    req: JobUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    jobs_col = db.get_collection("jobs") if hasattr(db, "get_collection") else db["jobs"]

    existing = await jobs_col.find_one({"_id": job_id, "user_id": user_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")

    updates = {}
    if req.title is not None:
        updates["title"] = req.title.strip()
    if req.company is not None:
        updates["company"] = req.company.strip()
    if req.location is not None:
        updates["location"] = req.location.strip()
    if req.job_description is not None:
        updates["job_description"] = req.job_description.strip()
    if req.required_experience_years is not None:
        updates["required_experience_years"] = float(req.required_experience_years)
    if req.status is not None:
        updates["status"] = req.status.strip()

    updates["updated_at"] = datetime.now().isoformat()
    await jobs_col.update_one({"_id": job_id, "user_id": user_id}, {"$set": updates})

    updated = await jobs_col.find_one({"_id": job_id, "user_id": user_id})
    return JobResponse(
        id=str(updated.get("_id")),
        user_id=user_id,
        title=updated.get("title", "Role"),
        company=updated.get("company", "Company"),
        location=updated.get("location", "Remote"),
        job_description=updated.get("job_description", ""),
        required_experience_years=float(updated.get("required_experience_years", 2.0)),
        status=updated.get("status", "Saved"),
        created_at=updated.get("created_at", datetime.now().isoformat()),
        updated_at=updated.get("updated_at", datetime.now().isoformat())
    )


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    jobs_col = db.get_collection("jobs") if hasattr(db, "get_collection") else db["jobs"]

    deleted = await jobs_col.delete_one({"_id": job_id, "user_id": user_id})
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")
    return {"message": "Job removed successfully."}
