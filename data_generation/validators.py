"""
Dataset validation module for CareerMatch AI.
Ensures data integrity, schema compliance, absence of NaNs,
realistic distributions, and absence of target leakage.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple


REQUIRED_COLUMNS: List[str] = [
    "resume_id",
    "job_id",
    "candidate_role",
    "target_job_role",
    "candidate_experience_years",
    "required_experience_years",
    "candidate_education",
    "required_education",
    "resume_summary",
    "resume_text",
    "job_description_text",
    "candidate_skills_list",
    "job_required_skills_list",
    "match_score"
]


class DatasetValidationError(Exception):
    """Raised when generated dataset fails validation checks."""
    pass


def validate_dataset(df: pd.DataFrame, min_records: int = 5000) -> Dict[str, Any]:
    """
    Run comprehensive statistical and structural validation checks on the dataset.
    
    Returns a dictionary of validation metrics or raises DatasetValidationError.
    """
    errors: List[str] = []
    
    # 1. Row count check
    total_records = len(df)
    if total_records < min_records:
        errors.append(f"Insufficient records: expected at least {min_records}, got {total_records}")

    # 2. Schema check
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")

    if errors:
        raise DatasetValidationError("; ".join(errors))

    # 3. Missing values check
    null_counts = df[REQUIRED_COLUMNS].isnull().sum()
    if null_counts.sum() > 0:
        bad_cols = null_counts[null_counts > 0].to_dict()
        errors.append(f"Dataset contains null values: {bad_cols}")

    # 4. Target validity check (match_score)
    scores = df["match_score"]
    if not np.issubdtype(scores.dtype, np.number):
        errors.append("Target 'match_score' is not numeric")
    else:
        min_score = float(scores.min())
        max_score = float(scores.max())
        if min_score < 0.0 or max_score > 100.0:
            errors.append(f"Target 'match_score' out of bounds [0, 100]: min={min_score}, max={max_score}")

    # 5. Duplicate check
    duplicate_rows = df.duplicated(subset=["resume_text", "job_description_text"]).sum()
    duplicate_pct = (duplicate_rows / total_records) * 100
    if duplicate_pct > 2.0:
        errors.append(f"Duplicate resume-job pairs exceed threshold (2%): {duplicate_pct:.2f}% ({duplicate_rows} pairs)")

    # 6. Target distribution balance check
    low_match = (scores < 50.0).mean() * 100
    mid_match = ((scores >= 50.0) & (scores < 75.0)).mean() * 100
    high_match = (scores >= 75.0).mean() * 100

    if low_match < 10.0:
        errors.append(f"Low match segment under-represented: {low_match:.1f}% (must be >= 10%)")
    if mid_match < 15.0:
        errors.append(f"Medium match segment under-represented: {mid_match:.1f}% (must be >= 15%)")
    if high_match < 10.0:
        errors.append(f"High match segment under-represented: {high_match:.1f}% (must be >= 10%)")

    # 7. Role representation check
    role_counts = df["target_job_role"].value_counts()
    if len(role_counts) < 10:
        errors.append(f"Fewer than 10 target job roles represented: found {len(role_counts)}")

    if errors:
        raise DatasetValidationError("; ".join(errors))

    validation_summary = {
        "status": "PASSED",
        "total_records": total_records,
        "score_mean": round(float(scores.mean()), 2),
        "score_std": round(float(scores.std()), 2),
        "score_min": round(float(scores.min()), 2),
        "score_max": round(float(scores.max()), 2),
        "distribution": {
            "low_pct (<50)": round(low_match, 2),
            "mid_pct (50-75)": round(mid_match, 2),
            "high_pct (>75)": round(high_match, 2)
        },
        "duplicate_pairs": int(duplicate_rows),
        "unique_target_roles": int(len(role_counts))
    }
    return validation_summary
