"""
SHAP Explainability Engine for CareerMatch AI.
Computes real Shapley additive feature attributions from the trained XGBoost model.
Zero hardcoding: all values calculated directly via shap.TreeExplainer.
Supports full 22-dimensional semantic, ontology, and experience feature set.
"""

import os
import pickle
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import shap

from ml.feature_engineering import FEATURE_NAMES


MODEL_PATH = os.path.join("models", "xgboost_match_model.pkl")

HUMAN_READABLE_NAMES = {
    "resume_job_semantic_similarity": "Overall Semantic Fit",
    "section_semantic_similarity": "Section-by-Section Fit",
    "technical_requirement_alignment": "Core Technical Alignment",
    "responsibility_alignment": "Past Duty Alignment",
    "role_alignment": "Job Title Semantic Match",
    "seniority_alignment": "Seniority Level Fit",
    "semantic_skill_coverage": "Demonstrated Skill Coverage",
    "explicit_skill_match_ratio": "Explicit Skill Matches",
    "related_skill_match_ratio": "Related / Transferable Skills",
    "true_skill_gap_ratio": "True Skill Gaps",
    "skill_ontology_coverage": "Ontology Skill Coverage",
    "missing_requirement_semantic_gap": "Requirement Deficiencies",
    "experience_alignment": "Years of Experience Fit",
    "experience_compatibility_score": "Experience Compatibility",
    "experience_exceeds_requirement": "Seniority Advantage (Exceeds Req)",
    "experience_gap": "Experience Tenurial Gap",
    "education_alignment": "Education & Degree Tier",
    "project_alignment": "Project-to-Role Alignment",
    "project_depth": "Technical Project Specificity",
    "project_skill_evidence": "Project-Backed Practical Evidence",
    "internship_alignment": "Practical Internship Foundation",
    "resume_completeness": "Resume Depth & Completeness"
}


class ModelExplainer:
    _instance = None

    def __new__(cls, model_path: str = MODEL_PATH):
        if cls._instance is None:
            cls._instance = super(ModelExplainer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path: str = MODEL_PATH):
        if self._initialized:
            return
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Run python -m ml.train_model first.")
        
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)
            
        print("[*] Initializing SHAP TreeExplainer for XGBoost...")
        self.explainer = shap.TreeExplainer(self.model)
        exp_val = self.explainer.expected_value
        if isinstance(exp_val, (list, np.ndarray)):
            self.base_value = float(np.ravel(exp_val)[0])
        else:
            self.base_value = float(exp_val)
        self._initialized = True
        print(f"[+] SHAP Explainer initialized (Base Score E[f(x)]: {self.base_value:.2f})")

    def explain_prediction(self, feature_dict: Dict[str, float]) -> Dict[str, Any]:
        """
        Computes local SHAP attributions for an individual candidate prediction.
        Returns exact feature impacts, direction, and structured waterfall data.
        """
        df_row = pd.DataFrame([[feature_dict[name] for name in FEATURE_NAMES]], columns=FEATURE_NAMES)
        
        # Calculate true SHAP values
        shap_values_raw = self.explainer.shap_values(df_row)
        
        if isinstance(shap_values_raw, list):
            sv = shap_values_raw[0][0]
        elif len(shap_values_raw.shape) == 2:
            sv = shap_values_raw[0]
        else:
            sv = shap_values_raw

        feature_impacts: List[Dict[str, Any]] = []
        for i, feat_name in enumerate(FEATURE_NAMES):
            raw_val = float(df_row.iloc[0, i])
            shap_val = float(sv[i])
            readable_label = HUMAN_READABLE_NAMES.get(feat_name, feat_name)

            if shap_val > 0.05:
                direction = "positive"
                text = f"{readable_label} bolstered the score by +{shap_val:.2f} points."
            elif shap_val < -0.05:
                direction = "negative"
                text = f"{readable_label} reduced the score by {shap_val:.2f} points."
            else:
                direction = "neutral"
                text = f"{readable_label} had minimal marginal impact ({shap_val:.2f} pts)."

            feature_impacts.append({
                "feature_name": feat_name,
                "display_name": readable_label,
                "feature_value": round(raw_val, 3),
                "shap_impact": round(shap_val, 3),
                "direction": direction,
                "explanation_text": text
            })

        # Sort by absolute SHAP magnitude
        feature_impacts.sort(key=lambda x: abs(x["shap_impact"]), reverse=True)

        # Top positive drivers and top negative detractors
        positives = [f for f in feature_impacts if f["direction"] == "positive"][:4]
        negatives = [f for f in feature_impacts if f["direction"] == "negative"][:4]

        return {
            "base_value": round(self.base_value, 2),
            "feature_impacts": feature_impacts,
            "top_positive_drivers": positives,
            "top_negative_detractors": negatives,
            "total_shap_adjustment": round(float(np.sum(sv)), 2)
        }


def get_explainer() -> ModelExplainer:
    return ModelExplainer()
