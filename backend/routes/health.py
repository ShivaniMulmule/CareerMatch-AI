"""
Health & Diagnostic Endpoints for CareerMatch AI.
Provides system runtime status, model version, storage provider, and database mode.
"""

import os
import json
from datetime import datetime
from fastapi import APIRouter
from database.db_client import get_current_db_mode
from storage.storage_client import get_current_storage_mode


router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("")
async def health_check():
    model_metadata = {}
    meta_path = os.path.join("models", "model_metadata.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                model_metadata = json.load(f)
        except Exception:
            pass

    return {
        "status": "HEALTHY",
        "product_name": "CareerMatch AI",
        "tagline": "Know Your Job Fit. Before You Apply.",
        "project_title": "Explainable AI-Based Resume Screening and Skill Gap Analysis System",
        "timestamp": datetime.now().isoformat(),
        "database_mode": get_current_db_mode(),
        "storage_mode": get_current_storage_mode(),
        "model_version": model_metadata.get("model_version", "1.0.0-xgboost"),
        "model_algorithm": "XGBRegressor + Sentence-BERT (all-MiniLM-L6-v2) + SHAP",
        "features_count": 14,
        "zero_keyword_matching_guarantee": True,
        "environment": "production" if os.getenv("ENVIRONMENT") == "production" else "development"
    }
