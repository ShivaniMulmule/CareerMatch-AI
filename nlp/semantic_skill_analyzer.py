"""
Evidence-Based Semantic Skill Gap Analyzer & Ontology Integrator for CareerMatch AI.
Combines three complementary layers:
  1. Explicit Skill Matching (exact canonical & alias recognition)
  2. Skill Ontology & Transferability Inference (hierarchical parent/related/framework mapping)
  3. Sentence-BERT Dense Vector Semantic Similarity with literal resume sentence quotes

Categorizes requirements into three distinct classes:
  A. EXPLICIT MATCH (Confidence: 1.0)
  B. RELATED / INFERRED MATCH (Confidence based on ontology transferability & S-BERT)
  C. TRUE GAP (No explicit or sufficiently strong related skill detected)

Never confuses conceptual mastery with specific framework expertise (e.g. Deep Learning != Keras).
"""

import json
import os
import re
from typing import Dict, Any, List, Tuple, Set
import numpy as np

from ml.embeddings import get_embedding_engine
from nlp.preprocessing import segment_sentences, clean_text
from nlp.skill_ontology import (
    SKILL_ONTOLOGY,
    ALIAS_TO_CANONICAL,
    normalize_skill_name,
    extract_explicit_skills_from_text,
    evaluate_skill_against_candidate
)


# Configurable Semantic Thresholds
STRONG_EVIDENCE_THRESHOLD = 0.68
PARTIAL_EVIDENCE_THRESHOLD = 0.48


def extract_job_requirements(job_description: str) -> List[str]:
    """
    Extracts individual requirement statements and technical skill concepts from the job description.
    Handles bullet points, comma-separated skill lists, and paragraph descriptions.
    """
    cleaned = clean_text(job_description)
    lines = cleaned.split("\n")
    requirements: List[str] = []

    # 1. Check for short skill lists, comma-separated skills, or single skills
    # e.g., "Kubernetes", "TensorFlow", "Machine Learning, Python, Keras"
    if len(cleaned.strip()) < 300 and len(cleaned.split("\n")) <= 5:
        parts = [p.strip() for p in re.split(r"[,;•\n\t]+", cleaned) if p.strip()]
        for p in parts:
            p_clean = re.sub(r"^(?:skills|requirements|qualifications|technologies|tools)\s*:\s*", "", p, flags=re.IGNORECASE).strip()
            if len(p_clean) >= 2 and p_clean.lower() not in ["and", "or", "etc", "none", "required"]:
                requirements.append(p_clean)
        if requirements:
            return requirements[:12]

    # 2. Check for explicit skill lines (e.g. "Requirements: Python, Keras, SQL")
    for line in lines:
        stripped = line.strip()
        if re.match(r"^(?:skills|technical skills|required skills|tools|technologies|competencies)\s*:\s*", stripped, re.IGNORECASE):
            content = re.sub(r"^(?:skills|technical skills|required skills|tools|technologies|competencies)\s*:\s*", "", stripped, flags=re.IGNORECASE)
            parts = [p.strip() for p in re.split(r"[,;•|]+", content) if len(p.strip()) >= 2]
            for p in parts:
                if p not in requirements:
                    requirements.append(p)

    # 3. Standard bullet extraction
    in_req_section = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        lower_line = stripped.lower()
        if any(h in lower_line for h in ["requirement", "qualification", "responsibilit", "what we're looking for", "capabilities", "must have", "what you'll need"]):
            in_req_section = True
            continue
        elif any(h in lower_line for h in ["about us", "benefits", "compensation", "perks", "company overview", "equal opportunity"]):
            in_req_section = False
            continue

        if in_req_section and (stripped.startswith(("-", "*", "•")) or re.match(r"^\d+[\.\)]", stripped)):
            content = re.sub(r"^[-*•\d\.\)\s]+", "", stripped).strip()
            if len(content) > 10 and content not in requirements:
                requirements.append(content)
        elif not in_req_section and (stripped.startswith(("-", "*", "•"))):
            content = re.sub(r"^[-*•\d\.\)\s]+", "", stripped).strip()
            if any(k in content.lower() for k in ["experience", "proficien", "knowledge", "skill", "build", "design", "develop", "model", "pipeline", "cloud", "api"]):
                if content not in requirements:
                    requirements.append(content)

    # 4. Fallback if no clean bullets were matched
    if not requirements:
        raw_sentences = segment_sentences(job_description)
        for s in raw_sentences:
            if any(k in s.lower() for k in ["experience", "knowledge", "ability", "proficien", "familiar", "responsible", "strong", "must have"]):
                requirements.append(s)
        if not requirements:
            requirements = [s.strip() for s in raw_sentences if len(s.strip()) >= 2]

    # Limit to top 10 distinct requirements
    seen = set()
    unique_reqs = []
    for r in requirements:
        r_short = r[:60].lower()
        if r_short not in seen:
            seen.add(r_short)
            unique_reqs.append(r)

    return unique_reqs[:10] if unique_reqs else [
        "Demonstrated experience building, training, and evaluating machine learning or software models.",
        "Proficiency in Python programming, clean coding, and automated software testing.",
        "Hands-on experience designing REST APIs and containerized microservice architectures.",
        "Experience collaborating in agile teams and version-controlled environments."
    ]


def analyze_semantic_skill_gaps(
    resume_text: str,
    job_description_text: str,
    project_text: str = "",
    requirements_override: List[str] = None
) -> Dict[str, Any]:
    """
    Executes hybrid skill evaluation combining:
      1. Explicit Skill Matching
      2. Skill Ontology Relationship & Transferability Analysis
      3. Sentence-BERT Dense Vector Cosine Similarity
      4. Literal Resume Quotation Citations

    Classifies every requirement into:
      - EXPLICIT MATCH
      - RELATED MATCH (or RELATED / INFERRED MATCH)
      - TRUE GAP
    """
    engine = get_embedding_engine()

    # 1. Identify requirements from Job Description
    requirements = requirements_override or extract_job_requirements(job_description_text)

    # 2. Extract candidate explicit skills and project context
    candidate_skills = extract_explicit_skills_from_text(resume_text, project_text)

    # 3. Segment candidate resume into candidate evidence sentences
    resume_sentences = segment_sentences(resume_text)
    if not resume_sentences:
        resume_sentences = [resume_text[:200]] if resume_text.strip() else ["Candidate background."]

    # 4. Batch embed requirements and resume sentences
    req_embeddings = engine.embed_batch(requirements)
    sentence_embeddings = engine.embed_batch(resume_sentences)

    # 5. Compute similarity matrix (N_requirements x M_sentences)
    sim_matrix = engine.batch_cosine_similarity(req_embeddings, sentence_embeddings)

    analyzed_items = []
    explicit_matches = []
    related_matches = []
    true_gaps = []

    strongly_demonstrated = []
    partially_demonstrated = []
    not_demonstrated = []

    for i, req in enumerate(requirements):
        row_sims = sim_matrix[i]
        best_idx = int(np.argmax(row_sims))
        best_sim = float(row_sims[best_idx])
        best_evidence_sentence = resume_sentences[best_idx].strip()

        # Evaluate against Skill Ontology & Candidate Profile
        eval_result = evaluate_skill_against_candidate(
            required_skill_str=req,
            candidate_skills=candidate_skills,
            resume_text=resume_text,
            project_text=project_text,
            semantic_sim_score=best_sim,
            evidence_sentence=best_evidence_sentence
        )

        status = eval_result["status"]  # "EXPLICIT MATCH", "RELATED MATCH", "TRUE GAP"
        confidence = eval_result["confidence"]
        reason = eval_result["reason"]
        evidence = eval_result["best_evidence"] or best_evidence_sentence
        inferred_from = eval_result.get("inferred_from")

        # Map to UI coverage status
        if status == "EXPLICIT MATCH":
            coverage_status = "Strongly Demonstrated"
            explicit_matches.append(req)
            strongly_demonstrated.append(req)
            is_gap = False
        elif status == "RELATED MATCH":
            coverage_status = "Partially Demonstrated"
            related_matches.append(req)
            partially_demonstrated.append(req)
            is_gap = False  # Crucial: Related skills are transferable, not hard missing gaps!
        else:
            coverage_status = "Not Clearly Demonstrated"
            true_gaps.append(req)
            not_demonstrated.append(req)
            is_gap = True

        analyzed_items.append({
            "requirement": req,
            "status": status,
            "match_category": eval_result.get("match_category", status),
            "coverage_status": coverage_status,
            "confidence": round(confidence, 2),
            "similarity_score": round(best_sim, 3),
            "inferred_from": inferred_from,
            "reason": reason,
            "best_evidence": evidence,
            "is_explicit": status == "EXPLICIT MATCH",
            "is_related": status == "RELATED MATCH",
            "is_gap": is_gap
        })

    # Summary metrics
    total_reqs = max(1, len(requirements))
    explicit_cnt = len(explicit_matches)
    related_cnt = len(related_matches)
    gap_cnt = len(true_gaps)

    explicit_ratio = float(explicit_cnt / total_reqs)
    related_ratio = float(related_cnt / total_reqs)
    gap_ratio = float(gap_cnt / total_reqs)

    # Ontology coverage: explicit gives 1.0, related transferable knowledge gives 0.70
    ontology_coverage = float(np.clip(
        (explicit_cnt * 1.0 + related_cnt * 0.70) / total_reqs,
        0.0, 1.0
    ))

    # Overall coverage percentage
    coverage_percentage = round(ontology_coverage * 100.0, 1)

    return {
        "total_requirements": total_reqs,
        "explicit_matches_count": explicit_cnt,
        "related_matches_count": related_cnt,
        "true_gaps_count": gap_cnt,
        "strongly_demonstrated_count": len(strongly_demonstrated),
        "partially_demonstrated_count": len(partially_demonstrated),
        "not_demonstrated_count": len(not_demonstrated),
        "explicit_skill_match_ratio": round(explicit_ratio, 4),
        "related_skill_match_ratio": round(related_ratio, 4),
        "true_skill_gap_ratio": round(gap_ratio, 4),
        "skill_ontology_coverage": round(ontology_coverage, 4),
        "coverage_percentage": coverage_percentage,
        "requirement_evaluations": analyzed_items,
        "explicit_matches": explicit_matches,
        "related_matches": related_matches,
        "true_gaps": true_gaps,
        "demonstrated_requirements": strongly_demonstrated,
        "partial_requirements": partially_demonstrated,
        "skill_gaps": true_gaps,
        "detected_candidate_skills": [c["canonical"] for c in candidate_skills.values()],
        "thresholds_used": {
            "explicit_match": "Canonical phrase/alias direct recognition (confidence: 1.0)",
            "related_match": "Ontology parent/adjacent/framework transfer or S-BERT sim >= 0.65",
            "true_gap": "No explicit or sufficiently strong related skill detected"
        }
    }
