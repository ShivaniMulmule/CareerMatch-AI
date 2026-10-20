"""
Recommendations API Endpoints for CareerMatch AI.
Provides stand-alone skill improvement recommendations and curated catalogs.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, List

from backend.dependencies.auth import get_current_user
from recommendations.recommendation_engine import load_learning_resources, generate_recommendations


router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("/catalog")
async def get_learning_catalog(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the full catalog of curated projects, courses, and certifications."""
    catalog = load_learning_resources()
    return catalog
