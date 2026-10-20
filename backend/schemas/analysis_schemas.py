"""
Analysis and evaluation Pydantic schemas for CareerMatch AI.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    resume_id: Optional[str] = None
    resume_text: Optional[str] = None
    job_id: Optional[str] = None
    job_title: Optional[str] = "Target Role"
    company: Optional[str] = "Target Company"
    job_description: Optional[str] = None


class DimensionScores(BaseModel):
    semantic_alignment: float
    capability_alignment: float
    experience_alignment: float
    education_alignment: float
    project_alignment: float


class FeatureImpact(BaseModel):
    feature_name: str
    display_name: str
    feature_value: float
    shap_impact: float
    direction: str
    explanation_text: str


class ShapExplanation(BaseModel):
    base_value: float
    feature_impacts: List[FeatureImpact]
    top_positive_drivers: List[FeatureImpact]
    top_negative_detractors: List[FeatureImpact]
    total_shap_adjustment: float


class RequirementEvaluation(BaseModel):
    requirement: str
    best_evidence: str
    similarity_score: float
    coverage_status: str
    is_gap: bool


class AnalysisResponse(BaseModel):
    id: str
    user_id: str
    resume_id: Optional[str] = None
    resume_filename: str
    job_id: Optional[str] = None
    job_title: str
    company: str
    match_score: float
    fit_category: str
    fit_description: str
    executive_reasoning: Optional[str] = None
    badge_color: str
    model_version: str
    dimension_scores: DimensionScores
    shap_explanation: ShapExplanation
    nlp_extractions: Dict[str, Any]
    recommendations: Dict[str, Any]
    created_at: str


class AnalysisListResponse(BaseModel):
    analyses: List[AnalysisResponse]
    total_count: int
