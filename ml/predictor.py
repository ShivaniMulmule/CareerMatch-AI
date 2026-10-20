"""
Inference Predictor for CareerMatch AI.
Combines NLP extraction, Sentence-BERT feature engineering, XGBoost regression,
SHAP explainability, and multi-layered skill ontology analysis into a single unified inference call.
"""

import os
import json
import pickle
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd

from ml.feature_engineering import FEATURE_NAMES, extract_features_from_texts
from ml.explainer import get_explainer


MODEL_PATH = os.path.join("models", "xgboost_match_model.pkl")
MODEL_META_PATH = os.path.join("models", "model_metadata.json")


def generate_executive_reasoning(
    match_score: float,
    fit_category: str,
    skill_gap_results: Dict[str, Any],
    exp_comp: Dict[str, Any]
) -> str:
    """Generates cohesive, evidence-backed narrative reasoning explaining the overall job fit."""
    explicit = skill_gap_results.get("explicit_matches", [])
    related = skill_gap_results.get("related_matches", [])
    gaps = skill_gap_results.get("true_gaps", [])

    parts = []

    # 1. Technical alignment paragraph
    if explicit:
        parts.append(
            f"The candidate demonstrates strong alignment with core technical requirements through explicit "
            f"verification of {', '.join(explicit[:4])}."
        )
    
    if related:
        parts.append(
            f"Additionally, the candidate possesses transferable conceptual competency in {', '.join(related[:3])} "
            f"inferred via adjacent domain background; these are treated as partial/related proficiencies rather than hard gaps."
        )

    if gaps:
        parts.append(
            f"Key unaddressed capabilities include {', '.join(gaps[:3])}, which represent genuine skill gaps where targeted portfolio additions or upskilling are recommended."
        )
    elif not related and not explicit:
        parts.append("Candidate technical background requires significant repositioning for this role.")

    # 2. Experience paragraph
    cand_yrs = exp_comp.get("candidate_years", 0.0)
    exp_status = exp_comp.get("status", "MATCH")
    if exp_status in ["MATCH", "STRONG MATCH"]:
        parts.append(
            f"On tenure, candidate brings {cand_yrs:.1f} years of relevant experience, satisfying the stated requirements with no experience penalty."
        )
    elif exp_status == "EXCEEDS PREFERRED RANGE":
        parts.append(
            f"On tenure, candidate brings {cand_yrs:.1f} years of seasoned experience, exceeding the preferred range without negative scoring."
        )
    elif exp_status == "EXPERIENCE GAP":
        min_y = exp_comp.get("jd_min_years", 0.0)
        parts.append(
            f"On tenure, candidate brings {cand_yrs:.1f} years vs minimum {min_y:.1f} years required, resulting in a moderate experience gap."
        )

    return " ".join(parts)


class MatchPredictor:
    _instance = None

    def __new__(cls, model_path: str = MODEL_PATH):
        if cls._instance is None:
            cls._instance = super(MatchPredictor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path: str = MODEL_PATH):
        if self._initialized:
            return
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Trained model not found at {model_path}. Please train via: python -m ml.train_model")

        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

        self.metadata = {}
        if os.path.exists(MODEL_META_PATH):
            with open(MODEL_META_PATH, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

        self.model_version = self.metadata.get("model_version", "2.0.0-xgboost-ontology")
        self._initialized = True
        print(f"[+] MatchPredictor loaded successfully (Version: {self.model_version})")

    def predict_match(
        self,
        resume_text: str,
        job_description_text: str,
        candidate_role: str = "",
        target_job_role: str = ""
    ) -> Dict[str, Any]:
        """
        Executes end-to-end inference pipeline:
        NLP Extractions -> S-BERT Embeddings -> 22 Semantic & Ontology Features
        -> XGBoost Match Score -> SHAP Explanation -> Executive Reasoning.
        """
        # 1. Feature extraction and NLP parsing
        features, nlp_data = extract_features_from_texts(
            resume_text=resume_text,
            job_description_text=job_description_text,
            candidate_role=candidate_role,
            target_job_role=target_job_role
        )

        # 2. XGBoost Prediction
        input_row = pd.DataFrame([[features[f] for f in FEATURE_NAMES]], columns=FEATURE_NAMES)
        predicted_score_raw = float(self.model.predict(input_row)[0])
        predicted_score = float(np.clip(predicted_score_raw, 5.0, 99.0))

        # 3. Dimensional Alignment Breakdown (0-100 scale for UI Radar/Bar charts)
        dimension_scores = {
            "semantic_alignment": round(features["resume_job_semantic_similarity"] * 100, 1),
            "capability_alignment": round(features["skill_ontology_coverage"] * 100, 1),
            "experience_alignment": round(features["experience_compatibility_score"] * 100, 1),
            "education_alignment": round(features["education_alignment"] * 100, 1),
            "project_alignment": round(features["project_alignment"] * 100, 1)
        }

        # 4. SHAP Explanation
        explainer = get_explainer()
        shap_analysis = explainer.explain_prediction(features)

        # 5. Fit Category
        if predicted_score >= 75.0:
            fit_category = "Strong Match"
            fit_description = "Outstanding profile alignment across technical capabilities, seniority, and projects."
            badge_color = "#137333"
        elif predicted_score >= 50.0:
            fit_category = "Moderate Match"
            fit_description = "Solid foundational competencies with addressable technical or experience gaps."
            badge_color = "#1A73E8"
        else:
            fit_category = "Low Match / Pivot Needed"
            fit_description = "Notable divergence between candidate profile and required core capabilities."
            badge_color = "#C04828"

        # 6. Executive Narrative Reasoning
        skill_gaps = nlp_data.get("skill_gap_results", {})
        exp_comp = nlp_data.get("experience_compatibility", {})
        executive_reasoning = generate_executive_reasoning(
            match_score=predicted_score,
            fit_category=fit_category,
            skill_gap_results=skill_gaps,
            exp_comp=exp_comp
        )

        return {
            "match_score": round(predicted_score, 1),
            "fit_category": fit_category,
            "fit_description": fit_description,
            "executive_reasoning": executive_reasoning,
            "badge_color": badge_color,
            "model_version": self.model_version,
            "dimension_scores": dimension_scores,
            "shap_explanation": shap_analysis,
            "features": features,
            "nlp_extractions": nlp_data
        }


def get_predictor() -> MatchPredictor:
    return MatchPredictor()
