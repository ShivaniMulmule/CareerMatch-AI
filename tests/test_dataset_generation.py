"""
Unit tests for CareerMatch AI Dataset Generation & Validation Pipeline.
"""

import os
import pytest
import pandas as pd
from data_generation.validators import validate_dataset, DatasetValidationError
from data_generation.dataset_config import ROLES, EXPERIENCE_LEVELS


def test_dataset_file_exists():
    path = os.path.join("data", "generated_resume_job_dataset.csv")
    assert os.path.exists(path), f"Generated dataset missing at {path}"


def test_dataset_schema_and_integrity():
    path = os.path.join("data", "generated_resume_job_dataset.csv")
    df = pd.read_csv(path)
    assert len(df) >= 5000, f"Expected at least 5000 records, found {len(df)}"

    summary = validate_dataset(df, min_records=5000)
    assert summary["status"] == "PASSED"
    assert summary["score_min"] >= 0.0
    assert summary["score_max"] <= 100.0


def test_dataset_target_distribution_balance():
    path = os.path.join("data", "generated_resume_job_dataset.csv")
    df = pd.read_csv(path)
    scores = df["match_score"]

    low_pct = (scores < 50.0).mean() * 100
    mid_pct = ((scores >= 50.0) & (scores < 75.0)).mean() * 100
    high_pct = (scores >= 75.0).mean() * 100

    # Ensure no bracket is empty or dominated
    assert low_pct >= 10.0, f"Low match bracket too low: {low_pct}%"
    assert mid_pct >= 15.0, f"Mid match bracket too low: {mid_pct}%"
    assert high_pct >= 10.0, f"High match bracket too low: {high_pct}%"
