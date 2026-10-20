"""
Analysis Endpoints for CareerMatch AI.
Executes the full pipeline:
PDF/Text -> NLP Extractor -> S-BERT Embeddings -> 14 Semantic Features -> XGBoost Regression -> SHAP -> Recommendations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from backend.schemas.analysis_schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisListResponse,
    DimensionScores,
    ShapExplanation,
    FeatureImpact
)
from backend.dependencies.auth import get_current_user
from database.db_client import get_database
from ml.predictor import get_predictor
from recommendations.recommendation_engine import generate_recommendations


router = APIRouter(prefix="/api/analyses", tags=["Analysis"])


@router.post("", response_model=AnalysisResponse)
async def analyze_match(
    req: AnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    resumes_col = db.get_collection("resumes") if hasattr(db, "get_collection") else db["resumes"]
    jobs_col = db.get_collection("jobs") if hasattr(db, "get_collection") else db["jobs"]
    analyses_col = db.get_collection("analyses") if hasattr(db, "get_collection") else db["analyses"]

    # 1. Resolve Resume Text
    resume_text = ""
    resume_filename = "Custom Text"
    if req.resume_id:
        resume_doc = await resumes_col.find_one({"_id": req.resume_id, "user_id": user_id})
        if not resume_doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified resume not found.")
        resume_text = resume_doc.get("extracted_text", "")
        resume_filename = resume_doc.get("original_filename", "resume.pdf")
    elif req.resume_text:
        resume_text = req.resume_text.strip()
    else:
        # Check if user has an active resume
        latest_resume = await resumes_col.find_one({"user_id": user_id}, sort=[("created_at", -1)])
        if latest_resume:
            resume_text = latest_resume.get("extracted_text", "")
            resume_filename = latest_resume.get("original_filename", "resume.pdf")
            req.resume_id = str(latest_resume.get("_id"))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please upload a resume or provide resume text to analyze."
            )

    if len(resume_text.strip()) < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text is too brief to analyze. Please provide a more complete resume."
        )

    # 2. Resolve Job Description
    job_desc = ""
    job_title = req.job_title or "Software Role"
    company = req.company or "Target Company"

    if req.job_id:
        job_doc = await jobs_col.find_one({"_id": req.job_id, "user_id": user_id})
        if job_doc:
            job_desc = job_doc.get("job_description", "")
            job_title = job_doc.get("title", job_title)
            company = job_doc.get("company", company)
    elif req.job_description:
        job_desc = req.job_description.strip()

    if len(job_desc.strip()) < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid Job Description with key responsibilities and requirements."
        )

    # 3. Execute ML Inference Pipeline
    predictor = get_predictor()
    prediction_result = predictor.predict_match(
        resume_text=resume_text,
        job_description_text=job_desc,
        target_job_role=job_title
    )

    # 4. Generate Actionable Recommendations
    skill_gaps = prediction_result["nlp_extractions"].get("skill_gap_results", {})
    recommendations = generate_recommendations(
        skill_gap_results=skill_gaps,
        match_score=prediction_result["match_score"],
        dimension_scores=prediction_result["dimension_scores"]
    )

    # 5. Store Record in Database
    analysis_doc = {
        "user_id": user_id,
        "resume_id": req.resume_id,
        "resume_filename": resume_filename,
        "job_id": req.job_id,
        "job_title": job_title,
        "company": company,
        "job_description_snippet": job_desc[:300],
        "match_score": prediction_result["match_score"],
        "fit_category": prediction_result["fit_category"],
        "fit_description": prediction_result["fit_description"],
        "executive_reasoning": prediction_result.get("executive_reasoning", ""),
        "badge_color": prediction_result["badge_color"],
        "model_version": prediction_result["model_version"],
        "dimension_scores": prediction_result["dimension_scores"],
        "shap_explanation": prediction_result["shap_explanation"],
        "nlp_extractions": prediction_result["nlp_extractions"],
        "recommendations": recommendations,
        "created_at": datetime.now().isoformat()
    }

    insert_res = await analyses_col.insert_one(analysis_doc)
    doc_id = str(insert_res.inserted_id)

    shap_data = prediction_result["shap_explanation"]
    shap_obj = ShapExplanation(
        base_value=shap_data["base_value"],
        feature_impacts=[FeatureImpact(**item) for item in shap_data["feature_impacts"]],
        top_positive_drivers=[FeatureImpact(**item) for item in shap_data["top_positive_drivers"]],
        top_negative_detractors=[FeatureImpact(**item) for item in shap_data["top_negative_detractors"]],
        total_shap_adjustment=shap_data["total_shap_adjustment"]
    )

    return AnalysisResponse(
        id=doc_id,
        user_id=user_id,
        resume_id=req.resume_id,
        resume_filename=resume_filename,
        job_id=req.job_id,
        job_title=job_title,
        company=company,
        match_score=prediction_result["match_score"],
        fit_category=prediction_result["fit_category"],
        fit_description=prediction_result["fit_description"],
        executive_reasoning=prediction_result.get("executive_reasoning", ""),
        badge_color=prediction_result["badge_color"],
        model_version=prediction_result["model_version"],
        dimension_scores=DimensionScores(**prediction_result["dimension_scores"]),
        shap_explanation=shap_obj,
        nlp_extractions=prediction_result["nlp_extractions"],
        recommendations=recommendations,
        created_at=analysis_doc["created_at"]
    )


@router.get("", response_model=AnalysisListResponse)
async def list_analyses(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    analyses_col = db.get_collection("analyses") if hasattr(db, "get_collection") else db["analyses"]

    records = await analyses_col.find({"user_id": user_id}, sort=[("created_at", -1)])
    results = []

    for r in records:
        shap_data = r.get("shap_explanation", {})
        shap_obj = ShapExplanation(
            base_value=shap_data.get("base_value", 70.0),
            feature_impacts=[FeatureImpact(**item) for item in shap_data.get("feature_impacts", [])],
            top_positive_drivers=[FeatureImpact(**item) for item in shap_data.get("top_positive_drivers", [])],
            top_negative_detractors=[FeatureImpact(**item) for item in shap_data.get("top_negative_detractors", [])],
            total_shap_adjustment=shap_data.get("total_shap_adjustment", 0.0)
        )
        results.append(
            AnalysisResponse(
                id=str(r.get("_id")),
                user_id=user_id,
                resume_id=r.get("resume_id"),
                resume_filename=r.get("resume_filename", "resume.pdf"),
                job_id=r.get("job_id"),
                job_title=r.get("job_title", "Role"),
                company=r.get("company", "Company"),
                match_score=float(r.get("match_score", 0.0)),
                fit_category=r.get("fit_category", "Evaluated"),
                fit_description=r.get("fit_description", ""),
                executive_reasoning=r.get("executive_reasoning", ""),
                badge_color=r.get("badge_color", "#7657B8"),
                model_version=r.get("model_version", "1.0.0"),
                dimension_scores=DimensionScores(**r.get("dimension_scores", {
                    "semantic_alignment": 0, "capability_alignment": 0, "experience_alignment": 0, "education_alignment": 0, "project_alignment": 0
                })),
                shap_explanation=shap_obj,
                nlp_extractions=r.get("nlp_extractions", {}),
                recommendations=r.get("recommendations", {}),
                created_at=r.get("created_at", datetime.now().isoformat())
            )
        )

    return AnalysisListResponse(analyses=results, total_count=len(results))


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    analyses_col = db.get_collection("analyses") if hasattr(db, "get_collection") else db["analyses"]

    r = await analyses_col.find_one({"_id": analysis_id, "user_id": user_id})
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis report not found.")

    shap_data = r.get("shap_explanation", {})
    shap_obj = ShapExplanation(
        base_value=shap_data.get("base_value", 70.0),
        feature_impacts=[FeatureImpact(**item) for item in shap_data.get("feature_impacts", [])],
        top_positive_drivers=[FeatureImpact(**item) for item in shap_data.get("top_positive_drivers", [])],
        top_negative_detractors=[FeatureImpact(**item) for item in shap_data.get("top_negative_detractors", [])],
        total_shap_adjustment=shap_data.get("total_shap_adjustment", 0.0)
    )

    return AnalysisResponse(
        id=str(r.get("_id")),
        user_id=user_id,
        resume_id=r.get("resume_id"),
        resume_filename=r.get("resume_filename", "resume.pdf"),
        job_id=r.get("job_id"),
        job_title=r.get("job_title", "Role"),
        company=r.get("company", "Company"),
        match_score=float(r.get("match_score", 0.0)),
        fit_category=r.get("fit_category", "Evaluated"),
        fit_description=r.get("fit_description", ""),
        executive_reasoning=r.get("executive_reasoning", ""),
        badge_color=r.get("badge_color", "#7657B8"),
        model_version=r.get("model_version", "1.0.0"),
        dimension_scores=DimensionScores(**r.get("dimension_scores", {
            "semantic_alignment": 0, "capability_alignment": 0, "experience_alignment": 0, "education_alignment": 0, "project_alignment": 0
        })),
        shap_explanation=shap_obj,
        nlp_extractions=r.get("nlp_extractions", {}),
        recommendations=r.get("recommendations", {}),
        created_at=r.get("created_at", datetime.now().isoformat())
    )


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    user_id = str(current_user.get("_id"))
    analyses_col = db.get_collection("analyses") if hasattr(db, "get_collection") else db["analyses"]

    deleted = await analyses_col.delete_one({"_id": analysis_id, "user_id": user_id})
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis report not found.")
    return {"message": "Analysis record deleted successfully."}
