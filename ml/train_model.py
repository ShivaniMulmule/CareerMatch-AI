"""
Model Training Pipeline for CareerMatch AI.
Loads the synthetic dataset, computes/validates 14 semantic features,
splits into train/test, trains an XGBRegressor, computes real evaluation metrics
(MAE, RMSE, R²), benchmarks against baseline semantic similarity,
and serializes artifacts to models/.

Command: python -m ml.train_model
"""

import os
import json
import time
from datetime import datetime
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb

from ml.feature_engineering import FEATURE_NAMES, extract_features_for_dataset
from data_generation.validators import validate_dataset


MODEL_DIR = "models"
DATA_PATH = "data/generated_resume_job_dataset.csv"
MODEL_PATH = os.path.join(MODEL_DIR, "xgboost_match_model.pkl")
FEATURE_META_PATH = os.path.join(MODEL_DIR, "feature_metadata.json")
METRICS_PATH = os.path.join(MODEL_DIR, "evaluation_metrics.json")
MODEL_META_PATH = os.path.join(MODEL_DIR, "model_metadata.json")


def train_model(data_path: str = DATA_PATH) -> dict:
    start_time = time.time()
    os.makedirs(MODEL_DIR, exist_ok=True)

    print("=" * 65)
    print("CAREERMATCH AI — XGBOOST REGRESSION TRAINING PIPELINE")
    print("=" * 65)

    # 1. Load Dataset
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}. Run python -m data_generation.generate_dataset first.")

    print(f"[*] Step 1: Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"    Loaded {len(df):,} records.")

    # 2. Validate Dataset
    print("[*] Step 2: Validating dataset integrity...")
    val_summary = validate_dataset(df, min_records=5000)
    print(f"    Integrity Status: {val_summary['status']}")

    # 3. Clean missing values if any
    df = df.dropna(subset=["match_score", "resume_text", "job_description_text"]).reset_index(drop=True)

    # 4. Generate Semantic Feature Matrix
    print("[*] Step 3: Computing 14 semantic and NLP features...")
    X = extract_features_for_dataset(df)
    y = df["match_score"].astype(float)

    # 5. Train / Test Split (80% train, 20% test)
    print("[*] Step 4: Partitioning into Train (80%) and Test (20%) sets (seed=42)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, shuffle=True
    )
    print(f"    Train records: {len(X_train):,} | Test records: {len(X_test):,}")

    # 6. Train XGBRegressor
    print("[*] Step 5: Training XGBRegressor...")
    model = xgb.XGBRegressor(
        n_estimators=250,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.1,
        reg_lambda=1.0,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    print("    Model training completed.")

    # 7. Evaluate on Test Set
    print("[*] Step 6: Evaluating model predictions on unseen test set...")
    y_pred = model.predict(X_test)
    y_pred = np.clip(y_pred, 0.0, 100.0)

    mae = float(mean_absolute_error(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, y_pred))

    # 5-fold Cross-Validation
    print("    Running 5-fold cross-validation...")
    kfold = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=kfold, scoring="r2")
    cv_r2_mean = float(np.mean(cv_scores))
    cv_r2_std = float(np.std(cv_scores))

    # 8. Baseline Comparison: Semantic Cosine Similarity alone (scaled 0-100)
    baseline_pred = X_test["resume_job_semantic_similarity"].values * 100.0
    baseline_mae = float(mean_absolute_error(y_test, baseline_pred))
    baseline_rmse = float(np.sqrt(mean_squared_error(y_test, baseline_pred)))
    baseline_r2 = float(r2_score(y_test, baseline_pred))

    print("-" * 65)
    print("MODEL EVALUATION RESULTS (REAL EXECUTION METRICS):")
    print(f"  MAE (Mean Absolute Error):   {mae:.3f} points")
    print(f"  RMSE (Root Mean Sq Error):   {rmse:.3f} points")
    print(f"  R² Score (Coefficient of Det): {r2:.4f}")
    print(f"  5-Fold CV R² Mean:           {cv_r2_mean:.4f} (+/- {cv_r2_std:.4f})")
    print("-" * 65)
    print("BASELINE COMPARISON (Baseline: Semantic Similarity Alone):")
    print(f"  Baseline MAE:                {baseline_mae:.3f} points")
    print(f"  Baseline RMSE:               {baseline_rmse:.3f} points")
    print(f"  Baseline R²:                 {baseline_r2:.4f}")
    print(f"  XGBoost R² Improvement:      +{(r2 - baseline_r2):.4f} ({((r2 - baseline_r2)/max(0.01, abs(baseline_r2))) * 100:.1f}%)")
    print("-" * 65)

    # 9. Feature Importances
    importances = model.feature_importances_
    feature_importance_dict = {
        name: round(float(imp), 4)
        for name, imp in sorted(zip(FEATURE_NAMES, importances), key=lambda x: x[1], reverse=True)
    }
    print("TOP FEATURE CONTRIBUTIONS (XGBOOST BUILT-IN IMPORTANCE):")
    for feat, imp in list(feature_importance_dict.items())[:6]:
        print(f"  - {feat:35s}: {imp:.4f}")

    # 10. Save Model Artifacts
    print(f"[*] Step 7: Saving model artifacts to {MODEL_DIR}...")
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"    Saved model to {MODEL_PATH}")

    feature_metadata = {
        "feature_names": FEATURE_NAMES,
        "feature_count": len(FEATURE_NAMES),
        "feature_importance_ranking": feature_importance_dict,
        "descriptions": {
            "resume_job_semantic_similarity": "Global dense vector cosine similarity (Sentence-BERT)",
            "section_semantic_similarity": "Structural section-level cosine similarity",
            "technical_requirement_alignment": "Mean alignment of candidate evidence to job requirements",
            "responsibility_alignment": "Past professional responsibilities alignment to job requirements",
            "role_alignment": "Semantic similarity of candidate role title to target position",
            "seniority_alignment": "Seniority tier match (junior, mid, senior, lead)",
            "semantic_skill_coverage": "Proportion of requirements meeting evidence threshold",
            "explicit_skill_match_ratio": "Proportion of job skills explicitly matched in candidate resume",
            "related_skill_match_ratio": "Proportion of skills inferred via ontology parent/adjacent relationships",
            "true_skill_gap_ratio": "Proportion of requirements with no explicit or inferred evidence",
            "skill_ontology_coverage": "Multi-tiered ontology coverage weighting explicit and transferable skills",
            "missing_requirement_semantic_gap": "Magnitude of semantic deficiency in least-evidenced requirements",
            "experience_alignment": "Candidate experience years vs job requirements ratio (non-penalizing for exceeding)",
            "experience_compatibility_score": "Dedicated experience compatibility score distinguishing matches and gaps",
            "experience_exceeds_requirement": "Binary indicator for candidate tenure exceeding minimum requirements",
            "experience_gap": "Numerical tenure deficit in years relative to minimum requirements",
            "education_alignment": "Degree level and quantitative qualification compatibility",
            "project_alignment": "Relevance of technical projects to target job responsibilities",
            "project_depth": "Depth, specificity, and density of technical projects",
            "project_skill_evidence": "Metric density and practical execution backing claimed skills",
            "internship_alignment": "Practical industry internship experience representation",
            "resume_completeness": "Structural presence of summary, skills, experience, projects, education"
        }
    }
    with open(FEATURE_META_PATH, "w", encoding="utf-8") as f:
        json.dump(feature_metadata, f, indent=2)

    evaluation_metrics = {
        "mae": round(mae, 3),
        "rmse": round(rmse, 3),
        "r2_score": round(r2, 4),
        "cv_r2_mean": round(cv_r2_mean, 4),
        "cv_r2_std": round(cv_r2_std, 4),
        "test_sample_count": len(y_test),
        "baseline_comparison": {
            "model_type": "Semantic Similarity Baseline (Single Dimension)",
            "baseline_mae": round(baseline_mae, 3),
            "baseline_rmse": round(baseline_rmse, 3),
            "baseline_r2": round(baseline_r2, 4),
            "xgboost_r2_gain": round(r2 - baseline_r2, 4)
        }
    }
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(evaluation_metrics, f, indent=2)

    model_metadata = {
        "product_name": "CareerMatch AI",
        "model_version": "1.0.0-xgboost-production",
        "training_timestamp": datetime.now().isoformat(),
        "dataset_version": "1.0.0",
        "feature_version": "1.0.0-14features",
        "algorithm": "XGBRegressor",
        "hyperparameters": {
            "n_estimators": 250,
            "max_depth": 5,
            "learning_rate": 0.08,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0
        },
        "metrics": evaluation_metrics
    }
    with open(MODEL_META_PATH, "w", encoding="utf-8") as f:
        json.dump(model_metadata, f, indent=2)

    elapsed = round(time.time() - start_time, 2)
    print("=" * 65)
    print(f"[+] Model training pipeline completed in {elapsed}s.")
    print("=" * 65)

    return model_metadata


if __name__ == "__main__":
    train_model()
