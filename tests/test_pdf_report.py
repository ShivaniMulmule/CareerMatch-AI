"""
Unit tests for PDF evaluation report compilation.
"""

from reports.pdf_report import build_analysis_pdf_report


def test_build_analysis_pdf_report():
    sample_analysis = {
        "_id": "test-analysis-12345",
        "job_title": "Machine Learning Engineer",
        "company": "NovaTech Labs",
        "resume_filename": "Candidate_CV.pdf",
        "match_score": 87.5,
        "fit_category": "Strong Match",
        "fit_description": "High alignment in machine learning architectures.",
        "model_version": "1.0.0-xgboost",
        "dimension_scores": {
            "semantic_alignment": 89.0,
            "capability_alignment": 91.0,
            "experience_alignment": 85.0,
            "education_alignment": 95.0,
            "project_alignment": 88.0
        },
        "shap_explanation": {
            "base_value": 71.0,
            "feature_impacts": [
                {
                    "display_name": "Core Technical Alignment",
                    "feature_value": 0.88,
                    "shap_impact": 4.25,
                    "direction": "positive",
                    "explanation_text": "Strong technical skills boosted score."
                }
            ]
        },
        "nlp_extractions": {
            "skill_gap_results": {
                "requirement_evaluations": [
                    {
                        "requirement": "Build predictive models with Python and Scikit-learn",
                        "coverage_status": "Strongly Demonstrated",
                        "best_evidence": "Engineered XGBoost predictive pipeline achieving 0.89 AUC.",
                        "similarity_score": 0.82
                    }
                ]
            }
        },
        "recommendations": {
            "summary": "Great match. Continue building cloud deployments.",
            "recommended_projects": [
                {"title": "FastAPI Deployment", "description": "Deploy ML model to AWS EC2."}
            ],
            "recommended_courses": [
                {"title": "MLOps Specialization", "provider": "DeepLearning.AI", "level": "Advanced", "closes_gap": "Cloud"}
            ]
        }
    }

    pdf_bytes = build_analysis_pdf_report(sample_analysis)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")
