"""
PDF Report Download Endpoint for CareerMatch AI.
Streams a ReportLab-generated evaluation dossier for an analysis record.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import Any, Dict

from backend.dependencies.auth import get_current_user
from database.db_client import get_database
from reports.pdf_report import build_analysis_pdf_report


router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/{analysis_id}")
async def download_analysis_report(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    analyses_col = db.get_collection("analyses") if hasattr(db, "get_collection") else db["analyses"]

    record = await analyses_col.find_one({"_id": analysis_id, "user_id": user_id})
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis record not found.")

    try:
        pdf_bytes = build_analysis_pdf_report(record)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF report: {str(e)}"
        )

    job_slug = str(record.get("job_title", "Evaluation")).replace(" ", "_")[:20]
    filename = f"CareerMatch_AI_Report_{job_slug}_{analysis_id[:6]}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )
