"""
Resume Management Endpoints for CareerMatch AI.
Handles PDF uploads, security validation, text extraction,
versioning, and metadata retrieval.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse, Response

from backend.schemas.resume_schemas import ResumeResponse, ResumeListResponse
from backend.dependencies.auth import get_current_user
from database.db_client import get_database
from storage.storage_client import get_storage
from nlp.pdf_reader import extract_text_from_pdf, PDFProcessingError
from nlp.experience_extractor import extract_experience_details
from nlp.education_extractor import extract_education_details
from nlp.preprocessing import segment_sections


router = APIRouter(prefix="/api/resumes", tags=["Resumes"])


@router.post("", response_model=ResumeResponse)
async def upload_resume(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    storage = get_storage()

    extracted_text = ""
    original_filename = "pasted_resume.txt"
    storage_meta = {
        "storage_provider": "INLINE",
        "file_id": "inline",
        "stored_filename": "inline",
        "file_size_bytes": 0,
        "download_url": "#"
    }

    if file:
        original_filename = file.filename or "resume.pdf"
        file_bytes = await file.read()

        if not original_filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format. Only PDF documents (.pdf) are permitted."
            )

        try:
            extracted_text, pdf_meta = extract_text_from_pdf(file_bytes, original_filename)
        except PDFProcessingError as pe:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(pe))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"PDF parsing failure: {str(e)}")

        storage_meta = storage.save_file(file_bytes, original_filename)
    elif raw_text and len(raw_text.strip()) > 30:
        extracted_text = raw_text.strip()
        storage_meta["file_size_bytes"] = len(extracted_text)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a PDF resume upload or paste resume text."
        )

    # Perform structural extractions
    sections = segment_sections(extracted_text)
    exp_details = extract_experience_details(extracted_text, sections.get("experience", ""))
    edu_details = extract_education_details(extracted_text, sections.get("education", ""))

    detected_role = exp_details["detected_titles"][0] if exp_details["detected_titles"] else "Candidate"

    resumes_col = db.get_collection("resumes") if hasattr(db, "get_collection") else db["resumes"]

    doc = {
        "user_id": user_id,
        "original_filename": original_filename,
        "stored_filename": storage_meta.get("stored_filename", "inline"),
        "storage_path": storage_meta.get("storage_path", "inline"),
        "file_size_bytes": storage_meta.get("file_size_bytes", len(extracted_text)),
        "char_count": len(extracted_text),
        "word_count": len(extracted_text.split()),
        "detected_role": detected_role,
        "extracted_text": extracted_text,
        "experience_summary": exp_details,
        "education_summary": edu_details,
        "storage_provider": storage_meta.get("storage_provider", "LOCAL_STORAGE"),
        "download_url": storage_meta.get("download_url", "#"),
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }

    insert_res = await resumes_col.insert_one(doc)
    doc_id = str(insert_res.inserted_id)

    return ResumeResponse(
        id=doc_id,
        user_id=user_id,
        original_filename=doc["original_filename"],
        stored_filename=doc["stored_filename"],
        file_size_bytes=doc["file_size_bytes"],
        char_count=doc["char_count"],
        word_count=doc["word_count"],
        detected_role=doc["detected_role"],
        experience_summary=doc["experience_summary"],
        education_summary=doc["education_summary"],
        extracted_text_preview=extracted_text[:400] + ("..." if len(extracted_text) > 400 else ""),
        storage_provider=doc["storage_provider"],
        download_url=doc["download_url"],
        created_at=doc["created_at"],
        is_active=True
    )


@router.get("", response_model=ResumeListResponse)
async def list_resumes(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    resumes_col = db.get_collection("resumes") if hasattr(db, "get_collection") else db["resumes"]
    
    records = await resumes_col.find({"user_id": user_id}, sort=[("created_at", -1)])
    
    results = [
        ResumeResponse(
            id=str(r.get("_id")),
            user_id=user_id,
            original_filename=r.get("original_filename", "resume.pdf"),
            stored_filename=r.get("stored_filename", ""),
            file_size_bytes=r.get("file_size_bytes", 0),
            char_count=r.get("char_count", 0),
            word_count=r.get("word_count", 0),
            detected_role=r.get("detected_role", "Candidate"),
            experience_summary=r.get("experience_summary"),
            education_summary=r.get("education_summary"),
            extracted_text_preview=r.get("extracted_text", "")[:400] + ("..." if len(r.get("extracted_text", "")) > 400 else ""),
            storage_provider=r.get("storage_provider", "LOCAL_STORAGE"),
            download_url=r.get("download_url", "#"),
            created_at=r.get("created_at", datetime.now().isoformat()),
            is_active=r.get("is_active", True)
        )
        for r in records
    ]

    return ResumeListResponse(resumes=results, total_count=len(results))


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    resumes_col = db.get_collection("resumes") if hasattr(db, "get_collection") else db["resumes"]
    
    r = await resumes_col.find_one({"_id": resume_id, "user_id": user_id})
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    return ResumeResponse(
        id=str(r.get("_id")),
        user_id=user_id,
        original_filename=r.get("original_filename", "resume.pdf"),
        stored_filename=r.get("stored_filename", ""),
        file_size_bytes=r.get("file_size_bytes", 0),
        char_count=r.get("char_count", 0),
        word_count=r.get("word_count", 0),
        detected_role=r.get("detected_role", "Candidate"),
        experience_summary=r.get("experience_summary"),
        education_summary=r.get("education_summary"),
        extracted_text_preview=r.get("extracted_text", "")[:500] + ("..." if len(r.get("extracted_text", "")) > 500 else ""),
        storage_provider=r.get("storage_provider", "LOCAL_STORAGE"),
        download_url=r.get("download_url", "#"),
        created_at=r.get("created_at", datetime.now().isoformat()),
        is_active=r.get("is_active", True)
    )


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    resumes_col = db.get_collection("resumes") if hasattr(db, "get_collection") else db["resumes"]
    
    r = await resumes_col.find_one({"_id": resume_id, "user_id": user_id})
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    # Delete physical file if local
    storage_path = r.get("storage_path")
    if storage_path and os.path.exists(storage_path):
        try:
            os.remove(storage_path)
        except Exception:
            pass

    await resumes_col.delete_one({"_id": resume_id, "user_id": user_id})
    return {"message": "Resume deleted successfully."}


@router.get("/download/{filename}")
async def download_file(filename: str):
    """Serve uploaded resume PDFs safely."""
    uploads_dir = os.path.abspath("uploads")
    safe_path = os.path.abspath(os.path.join(uploads_dir, filename))
    # Prevent path traversal
    if not safe_path.startswith(uploads_dir) or not os.path.exists(safe_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
    return FileResponse(safe_path, media_type="application/pdf", filename=filename)
