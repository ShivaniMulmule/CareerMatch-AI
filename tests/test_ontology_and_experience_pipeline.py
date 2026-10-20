"""
Automated Test Suite for Skill Ontology, Transferability Reasoning,
and Fair Experience Compatibility Pipeline.

Implements all 9 test cases mandated by the user specifications:
  TEST 1: Resume: "Deep Learning, CNN, Python" / JD: "Machine Learning, Python, Keras"
          Expected: Python=EXPLICIT, ML=RELATED, Keras=RELATED (not a hard missing skill).
  TEST 2: Resume: "Python, Pandas, NumPy, Machine Learning" / JD: "Python, Pandas, NumPy"
          Expected: All three = EXPLICIT MATCH.
  TEST 3: Resume: "React, JavaScript" / JD: "Kubernetes"
          Expected: Kubernetes = TRUE GAP.
  TEST 4: Resume: "Deep Learning" / JD: "TensorFlow"
          Expected: TensorFlow = RELATED/PARTIAL MATCH, NOT explicit match.
  TEST 5: Candidate 1 yr / JD "No experience required"
          Expected: MATCH, no negative penalty.
  TEST 6: Candidate 1 yr / JD "0-1 years"
          Expected: MATCH.
  TEST 7: Candidate 3 yrs / JD "0-2 years"
          Expected: EXCEEDS PREFERRED RANGE (not classified as failure).
  TEST 8: Candidate 1 yr / JD "Minimum 3 years"
          Expected: EXPERIENCE GAP.
  TEST 9: Candidate 1 yr / JD "Freshers welcome"
          Expected: MATCH.
"""

import pytest
from nlp.skill_ontology import (
    extract_explicit_skills_from_text,
    evaluate_skill_against_candidate
)
from nlp.experience_extractor import (
    experience_compatibility,
    parse_jd_experience_requirements
)
from nlp.semantic_skill_analyzer import analyze_semantic_skill_gaps
from ml.predictor import get_predictor


def test_case_1_deep_learning_implies_ml_and_related_keras():
    """
    TEST 1:
    Resume: "Deep Learning, CNN, Python"
    JD: "Machine Learning, Python, Keras"
    Expected:
      Python = EXPLICIT MATCH
      Machine Learning = RELATED MATCH
      Keras = RELATED/PARTIAL MATCH (Keras should NOT be classified as a hard missing skill).
    """
    resume = "Deep Learning, CNN, Python"
    jd = "Machine Learning, Python, Keras"

    results = analyze_semantic_skill_gaps(resume, jd)
    evals_by_req = {item["requirement"].lower(): item for item in results["requirement_evaluations"]}

    # Python
    assert "python" in evals_by_req
    py_eval = evals_by_req["python"]
    assert py_eval["status"] == "EXPLICIT MATCH"
    assert py_eval["confidence"] == 1.0

    # Machine Learning
    assert "machine learning" in evals_by_req
    ml_eval = evals_by_req["machine learning"]
    assert ml_eval["status"] == "RELATED MATCH"
    assert ml_eval["is_explicit"] is False
    assert ml_eval["is_gap"] is False

    # Keras: Must be RELATED/PARTIAL, NOT hard missing/true gap!
    assert "keras" in evals_by_req
    keras_eval = evals_by_req["keras"]
    assert keras_eval["status"] == "RELATED MATCH"
    assert keras_eval["is_explicit"] is False
    assert keras_eval["is_gap"] is False
    assert "deep learning" in keras_eval["reason"].lower()
    assert "keras is not explicitly" in keras_eval["reason"].lower()


def test_case_2_explicit_skill_match_python_pandas_numpy():
    """
    TEST 2:
    Resume: "Python, Pandas, NumPy, Machine Learning"
    JD: "Python, Pandas, NumPy"
    Expected: All three = EXPLICIT MATCH.
    """
    resume = "Python, Pandas, NumPy, Machine Learning"
    jd = "Python, Pandas, NumPy"

    results = analyze_semantic_skill_gaps(resume, jd)
    evals = {item["requirement"].lower(): item for item in results["requirement_evaluations"]}

    for skill in ["python", "pandas", "numpy"]:
        assert skill in evals
        assert evals[skill]["status"] == "EXPLICIT MATCH"
        assert evals[skill]["confidence"] == 1.0


def test_case_3_true_gap_react_vs_kubernetes():
    """
    TEST 3:
    Resume: "React, JavaScript"
    JD: "Kubernetes"
    Expected: Kubernetes = TRUE GAP.
    """
    resume = "React, JavaScript"
    jd = "Kubernetes"

    results = analyze_semantic_skill_gaps(resume, jd)
    evals = {item["requirement"].lower(): item for item in results["requirement_evaluations"]}

    assert "kubernetes" in evals
    k8s_eval = evals["kubernetes"]
    assert k8s_eval["status"] == "TRUE GAP"
    assert k8s_eval["is_gap"] is True


def test_case_4_deep_learning_vs_tensorflow_related_not_explicit():
    """
    TEST 4:
    Resume: "Deep Learning"
    JD: "TensorFlow"
    Expected: TensorFlow = RELATED/PARTIAL MATCH, NOT explicit match.
    """
    resume = "Deep Learning"
    jd = "TensorFlow"

    results = analyze_semantic_skill_gaps(resume, jd)
    evals = {item["requirement"].lower(): item for item in results["requirement_evaluations"]}

    assert "tensorflow" in evals
    tf_eval = evals["tensorflow"]
    assert tf_eval["status"] == "RELATED MATCH"
    assert tf_eval["is_explicit"] is False
    assert tf_eval["is_gap"] is False
    assert "deep learning" in tf_eval["reason"].lower()
    assert "not explicitly" in tf_eval["reason"].lower()


def test_case_5_experience_no_experience_required_no_negative_penalty():
    """
    TEST 5:
    Candidate: 1 year experience
    JD: "No experience required"
    Expected: Experience = MATCH, No negative penalty.
    """
    jd_reqs = parse_jd_experience_requirements("No experience required")
    res = experience_compatibility(
        candidate_experience=1.0,
        jd_min_experience=jd_reqs["min_years"],
        jd_max_experience=jd_reqs["max_years"],
        is_freshers_welcome=jd_reqs["is_freshers_welcome"]
    )
    assert res["status"] in ["MATCH", "STRONG MATCH"]
    assert res["score"] == 1.0
    assert res["is_gap"] is False


def test_case_6_experience_0_to_1_years_match():
    """
    TEST 6:
    Candidate: 1 year experience
    JD: "0-1 years"
    Expected: Experience = MATCH.
    """
    jd_reqs = parse_jd_experience_requirements("0-1 years")
    res = experience_compatibility(
        candidate_experience=1.0,
        jd_min_experience=jd_reqs["min_years"],
        jd_max_experience=jd_reqs["max_years"]
    )
    assert res["status"] == "MATCH"
    assert res["score"] == 1.0
    assert res["is_gap"] is False


def test_case_7_experience_3_years_vs_0_to_2_years_exceeds_preferred_range_no_failure():
    """
    TEST 7:
    Candidate: 3 years experience
    JD: "0-2 years"
    Expected:
      Do NOT classify as an experience failure.
      Use: "EXCEEDS PREFERRED RANGE" or a neutral/positive compatibility status.
    """
    jd_reqs = parse_jd_experience_requirements("0-2 years")
    res = experience_compatibility(
        candidate_experience=3.0,
        jd_min_experience=jd_reqs["min_years"],
        jd_max_experience=jd_reqs["max_years"]
    )
    assert res["status"] == "EXCEEDS PREFERRED RANGE"
    assert res["score"] >= 0.90
    assert res["is_gap"] is False


def test_case_8_experience_1_year_vs_min_3_years_gap():
    """
    TEST 8:
    Candidate: 1 year experience
    JD: "Minimum 3 years"
    Expected: EXPERIENCE GAP.
    """
    jd_reqs = parse_jd_experience_requirements("Minimum 3 years")
    res = experience_compatibility(
        candidate_experience=1.0,
        jd_min_experience=jd_reqs["min_years"],
        jd_max_experience=jd_reqs["max_years"]
    )
    assert res["status"] == "EXPERIENCE GAP"
    assert res["is_gap"] is True
    assert res["score"] < 0.50


def test_case_9_experience_freshers_welcome_match():
    """
    TEST 9:
    Candidate: 1 year experience
    JD: "Freshers welcome"
    Expected: MATCH.
    """
    jd_reqs = parse_jd_experience_requirements("Freshers welcome")
    res = experience_compatibility(
        candidate_experience=1.0,
        jd_min_experience=jd_reqs["min_years"],
        jd_max_experience=jd_reqs["max_years"],
        is_freshers_welcome=jd_reqs["is_freshers_welcome"]
    )
    assert res["status"] in ["MATCH", "STRONG MATCH"]
    assert res["score"] == 1.0
    assert res["is_gap"] is False


def test_end_to_end_pipeline_with_executive_reasoning():
    """
    Verifies end-to-end predictor with executive reasoning and SHAP explainability.
    """
    predictor = get_predictor()
    resume = (
        "Machine Learning Engineer with 2.5 years experience in Python, Scikit-Learn, and Deep Learning.\n"
        "Built predictive models and computer vision pipelines using CNN."
    )
    jd = (
        "Seeking an ML Engineer with experience in Machine Learning, Python, and Keras.\n"
        "Experience: 2+ years required."
    )

    result = predictor.predict_match(resume, jd, target_job_role="ML Engineer")
    assert "match_score" in result
    assert "executive_reasoning" in result
    assert len(result["executive_reasoning"]) > 20
    assert "shap_explanation" in result
    assert len(result["shap_explanation"]["feature_impacts"]) == 22
