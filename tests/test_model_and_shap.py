"""
End-to-End test verifying XGBoost model prediction and SHAP explainability.
"""

import os
import pytest
from ml.predictor import get_predictor
from ml.explainer import get_explainer
from recommendations.recommendation_engine import generate_recommendations


def test_model_and_shap_pipeline_execution():
    model_path = os.path.join("models", "xgboost_match_model.pkl")
    assert os.path.exists(model_path), f"Trained model missing at {model_path}"

    sample_resume = """
    NAME: Priya Sharma
    ROLE: Machine Learning Engineer
    EXPERIENCE: 3.5 years of industry experience
    EDUCATION: B.Tech in Artificial Intelligence & Data Science, IIT Bombay (2022)

    SUMMARY:
    Results-driven Machine Learning Engineer with 3.5 years of experience developing predictive algorithms,
    deploying microservice endpoints using FastAPI, and optimizing gradient boosted tree models.

    TECHNICAL SKILLS:
    Python, Scikit-Learn, PyTorch, XGBoost, Docker, FastAPI, AWS EC2, SQL, Git, CI/CD

    EXPERIENCE:
    ML Engineer at NovaTech AI Labs (2022 - Present)
    - Developed and deployed XGBoost tabular fraud detection models on AWS EC2, reducing false positives by 18%.
    - Containerized ML inference services with Docker and FastAPI, maintaining sub-45ms p95 latency.
    - Integrated SHAP TreeExplainer to provide model interpretability to fraud investigators.
    """

    sample_job = """
    COMPANY: Apex FinTech
    POSITION: Machine Learning Engineer
    REQUIRED EXPERIENCE: 3+ years
    EDUCATION REQUIREMENT: B.Tech in Computer Science, Data Science, or related engineering discipline

    RESPONSIBILITIES:
    - Build, train, and deploy robust machine learning and deep learning pipelines.
    - Collaborate with backend engineers to deploy containerized REST APIs in cloud environments.
    - Implement explainable AI practices to interpret complex prediction models.

    QUALIFICATIONS:
    - Demonstrated experience in Python, Scikit-Learn, XGBoost, and PyTorch.
    - Experience deploying ML models using FastAPI and Docker on AWS.
    - Minimum 3 years of hands-on experience in machine learning production systems.
    """

    predictor = get_predictor()
    result = predictor.predict_match(
        resume_text=sample_resume,
        job_description_text=sample_job,
        candidate_role="Machine Learning Engineer",
        target_job_role="Machine Learning Engineer"
    )

    # Assertions
    assert "match_score" in result
    assert 50.0 <= result["match_score"] <= 100.0, f"Unexpected score: {result['match_score']}"
    assert result["fit_category"] in ["Strong Match", "Moderate Match"]

    # SHAP Explanations
    shap_data = result["shap_explanation"]
    assert "base_value" in shap_data
    assert len(shap_data["feature_impacts"]) == 22
    assert len(shap_data["top_positive_drivers"]) > 0

    # Skill Gap & Evidence
    skill_evals = result["nlp_extractions"]["skill_gap_results"]["requirement_evaluations"]
    assert len(skill_evals) > 0
    # Check that real evidence quote is present
    has_evidence = any("XGBoost" in item["best_evidence"] or "FastAPI" in item["best_evidence"] for item in skill_evals)
    assert has_evidence, "Expected real candidate resume sentence as evidence"

    # Recommendations
    recs = generate_recommendations(
        skill_gap_results=result["nlp_extractions"]["skill_gap_results"],
        match_score=result["match_score"],
        dimension_scores=result["dimension_scores"]
    )
    assert "recommended_projects" in recs
    assert len(recs["recommended_projects"]) > 0
