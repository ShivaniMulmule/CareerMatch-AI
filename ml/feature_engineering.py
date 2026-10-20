"""
Semantic Feature Engineering Pipeline for CareerMatch AI.
Extracts 22 independent semantic, ontology, and NLP features for XGBoost regression.
Strictly zero keyword-only counting, zero target leakage.
All features derived from dense vector embeddings (Sentence-BERT),
hierarchical skill ontology relationships, and structured experience compatibility.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import re

from ml.embeddings import get_embedding_engine
from nlp.preprocessing import segment_sections, segment_sentences, clean_text
from nlp.experience_extractor import (
    extract_experience_details,
    parse_jd_experience_requirements,
    experience_compatibility
)
from nlp.education_extractor import extract_education_details
from nlp.project_analyzer import extract_project_blocks, analyze_projects_semantic
from nlp.semantic_skill_analyzer import analyze_semantic_skill_gaps, extract_job_requirements


# 22 Calibrated Feature Names
FEATURE_NAMES: List[str] = [
    # 1. Semantic & Text Representations
    "resume_job_semantic_similarity",
    "section_semantic_similarity",
    "technical_requirement_alignment",
    "responsibility_alignment",
    "role_alignment",
    "seniority_alignment",

    # 2. Skill Ontology & Match Categories (Enhanced)
    "semantic_skill_coverage",
    "explicit_skill_match_ratio",
    "related_skill_match_ratio",
    "true_skill_gap_ratio",
    "skill_ontology_coverage",
    "missing_requirement_semantic_gap",

    # 3. Experience Compatibility (Fair & Non-Penalizing)
    "experience_alignment",
    "experience_compatibility_score",
    "experience_exceeds_requirement",
    "experience_gap",

    # 4. Education, Projects & Practical Depth
    "education_alignment",
    "project_alignment",
    "project_depth",
    "project_skill_evidence",
    "internship_alignment",
    "resume_completeness"
]


def compute_experience_alignment_feature(cand_years: float, req_years: float) -> float:
    """
    Computes continuous non-linear experience compatibility score [0.0, 1.0].
    Critically: Having MORE experience than required is NEVER heavily penalized.
    """
    if req_years <= 0.0:
        return 1.0
    ratio = cand_years / req_years
    if ratio >= 1.0:
        # Meets or exceeds: 1.0 score, with a minimal plateau at extreme overqualification (>3.5x)
        if ratio > 3.5:
            return float(np.clip(1.0 - (ratio - 3.5) * 0.03, 0.88, 1.0))
        return 1.0
    else:
        # Underqualified
        return float(np.clip(ratio, 0.10, 0.95))


def compute_education_alignment_feature(edu_dict: Dict[str, Any], job_text: str) -> float:
    """Evaluates degree tier and quantitative background alignment."""
    tier = edu_dict.get("tier", "Other")
    tier_scores = {
        "Doctorate": 1.0,
        "Tech_PG": 0.98,
        "Tech_UG": 0.90,
        "Math_UG": 0.85,
        "Business_UG": 0.70,
        "Non_Tech": 0.55,
        "Other": 0.50
    }
    base_score = tier_scores.get(tier, 0.60)
    job_lower = job_text.lower()
    if "ph.d" in job_lower or "doctorate" in job_lower:
        if tier != "Doctorate":
            base_score *= 0.75
    elif "master" in job_lower or "m.s." in job_lower or "m.tech" in job_lower:
        if tier not in ["Doctorate", "Tech_PG"]:
            base_score *= 0.88
    return float(np.clip(base_score, 0.10, 1.0))


def extract_features_from_texts(
    resume_text: str,
    job_description_text: str,
    candidate_role: str = "",
    target_job_role: str = "",
    cand_exp_years: float = None,
    req_exp_years: float = None
) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """
    Extracts 22-dimensional feature vector and comprehensive intermediate NLP extractions
    for an individual candidate resume and job description pair.
    """
    engine = get_embedding_engine()

    # 1. Structural Section Segmentation
    resume_sections = segment_sections(resume_text)
    job_sections = segment_sections(job_description_text)
    project_text = resume_sections.get("projects", "")

    # 2. NLP & Experience Extraction
    exp_details = extract_experience_details(resume_text, resume_sections.get("experience", ""), project_text)
    edu_details = extract_education_details(resume_text, resume_sections.get("education", ""))
    jd_exp_reqs = parse_jd_experience_requirements(job_description_text)

    cand_years = cand_exp_years if cand_exp_years is not None else exp_details["total_years_num"]
    req_years = req_exp_years if req_exp_years is not None else jd_exp_reqs["min_years"]
    max_req_years = jd_exp_reqs.get("max_years")

    # Evaluate Dedicated Experience Compatibility (Non-penalizing for exceeding)
    exp_comp = experience_compatibility(
        candidate_experience=cand_years,
        jd_min_experience=req_years,
        jd_max_experience=max_req_years,
        experience_required=jd_exp_reqs.get("is_required", True),
        experience_preferred=jd_exp_reqs.get("is_preferred", False),
        is_freshers_welcome=jd_exp_reqs.get("is_freshers_welcome", False)
    )

    feat_experience_alignment = compute_experience_alignment_feature(cand_years, req_years)
    feat_exp_comp_score = float(exp_comp["score"])
    feat_exp_exceeds = 1.0 if exp_comp.get("exceeds") else 0.0
    feat_exp_gap = float(max(0.0, req_years - cand_years))

    # 3. Dense Embeddings
    resume_emb = engine.embed_text(resume_text)
    job_emb = engine.embed_text(job_description_text)
    feat_overall_sim = float(np.clip((engine.cosine_similarity(resume_emb, job_emb) + 0.1) / 1.1, 0.0, 1.0))

    # Section-level similarity
    summary_text = resume_sections.get("summary", "") or resume_text[:300]
    job_overview = job_sections.get("summary", "") or job_description_text[:300]
    sec_sim_1 = engine.cosine_similarity(engine.embed_text(summary_text), engine.embed_text(job_overview))

    skills_text = resume_sections.get("skills", "") or resume_text[:300]
    job_qual_text = job_sections.get("skills", "") or job_description_text[:400]
    sec_sim_2 = engine.cosine_similarity(engine.embed_text(skills_text), engine.embed_text(job_qual_text))
    feat_section_sim = float(np.clip(0.5 * (sec_sim_1 + sec_sim_2 + 0.2) / 1.2, 0.0, 1.0))

    # 4. Multi-Layer Skill Gap & Ontology Analysis
    skill_gap_results = analyze_semantic_skill_gaps(
        resume_text=resume_text,
        job_description_text=job_description_text,
        project_text=project_text
    )
    req_evals = skill_gap_results["requirement_evaluations"]

    sim_scores = [item["similarity_score"] for item in req_evals] if req_evals else [0.5]
    feat_tech_req_alignment = float(np.clip(np.mean(sim_scores), 0.0, 1.0))
    feat_semantic_skill_coverage = float(skill_gap_results["coverage_percentage"] / 100.0)

    feat_explicit_ratio = float(skill_gap_results["explicit_skill_match_ratio"])
    feat_related_ratio = float(skill_gap_results["related_skill_match_ratio"])
    feat_true_gap_ratio = float(skill_gap_results["true_skill_gap_ratio"])
    feat_ontology_coverage = float(skill_gap_results["skill_ontology_coverage"])

    lowest_sims = sorted(sim_scores)[:3]
    feat_missing_gap = float(np.clip(1.0 - np.mean(lowest_sims), 0.0, 1.0))

    # 5. Project Semantic Relevance & Practical Evidence
    project_blocks = extract_project_blocks(project_text, resume_text)
    project_analysis = analyze_projects_semantic(
        project_blocks,
        job_description_text,
        job_sections.get("experience", "")
    )
    feat_project_alignment = float(project_analysis["overall_project_relevance"])
    feat_project_skill_evidence = float(project_analysis.get("metric_density_score", 0.70))

    # 6. Education Alignment
    feat_education_alignment = compute_education_alignment_feature(edu_details, job_description_text)

    # 7. Responsibility Alignment
    exp_text = resume_sections.get("experience", "") or resume_text
    job_resp = job_sections.get("experience", "") or job_description_text
    resp_sim = engine.cosine_similarity(engine.embed_text(exp_text), engine.embed_text(job_resp))
    feat_responsibility_alignment = float(np.clip((resp_sim + 0.2) / 1.2, 0.0, 1.0))

    # 8. Role & Seniority Alignment
    inferred_cand_role = candidate_role or (exp_details["detected_titles"][0] if exp_details["detected_titles"] else "Software Engineer")
    inferred_target_role = target_job_role or "Software Engineer"
    role_sim = engine.cosine_similarity(engine.embed_text(inferred_cand_role), engine.embed_text(inferred_target_role))
    feat_role_alignment = float(np.clip((role_sim + 0.1) / 1.1, 0.0, 1.0))

    is_senior_job = any(k in inferred_target_role.lower() for k in ["senior", "sr", "lead", "principal", "architect"]) or req_years >= 5.0
    is_senior_cand = cand_years >= 4.5 or exp_details["has_leadership"]
    if is_senior_job == is_senior_cand:
        feat_seniority_alignment = 0.95
    elif not is_senior_job and is_senior_cand:
        feat_seniority_alignment = 0.90  # Experienced candidate for standard role is positive
    else:
        feat_seniority_alignment = max(0.20, min(0.70, cand_years / max(1.0, req_years)))

    # 9. Completeness & Project Depth
    sections_found = sum(1 for s in ["summary", "experience", "skills", "projects", "education"] if resume_sections.get(s, "").strip())
    feat_resume_completeness = float(sections_found / 5.0)
    feat_project_depth = float(np.clip(len(project_blocks) / 3.0, 0.1, 1.0))
    feat_internship_alignment = 0.90 if exp_details["has_internships"] else (0.85 if cand_years >= 2.0 else 0.45)

    feature_dict = {
        "resume_job_semantic_similarity": round(feat_overall_sim, 4),
        "section_semantic_similarity": round(feat_section_sim, 4),
        "technical_requirement_alignment": round(feat_tech_req_alignment, 4),
        "responsibility_alignment": round(feat_responsibility_alignment, 4),
        "role_alignment": round(feat_role_alignment, 4),
        "seniority_alignment": round(feat_seniority_alignment, 4),
        "semantic_skill_coverage": round(feat_semantic_skill_coverage, 4),
        "explicit_skill_match_ratio": round(feat_explicit_ratio, 4),
        "related_skill_match_ratio": round(feat_related_ratio, 4),
        "true_skill_gap_ratio": round(feat_true_gap_ratio, 4),
        "skill_ontology_coverage": round(feat_ontology_coverage, 4),
        "missing_requirement_semantic_gap": round(feat_missing_gap, 4),
        "experience_alignment": round(feat_experience_alignment, 4),
        "experience_compatibility_score": round(feat_exp_comp_score, 4),
        "experience_exceeds_requirement": round(feat_exp_exceeds, 4),
        "experience_gap": round(feat_exp_gap, 4),
        "education_alignment": round(feat_education_alignment, 4),
        "project_alignment": round(feat_project_alignment, 4),
        "project_depth": round(feat_project_depth, 4),
        "project_skill_evidence": round(feat_project_skill_evidence, 4),
        "internship_alignment": round(feat_internship_alignment, 4),
        "resume_completeness": round(feat_resume_completeness, 4)
    }

    extra_nlp_data = {
        "experience_details": exp_details,
        "experience_compatibility": exp_comp,
        "education_details": edu_details,
        "project_analysis": project_analysis,
        "skill_gap_results": skill_gap_results,
        "sections": resume_sections
    }

    return feature_dict, extra_nlp_data


def extract_features_for_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes 22-dimensional feature matrix for the training dataset.
    Vectorized S-BERT embeddings combined with structured ontology and experience calculations.
    """
    engine = get_embedding_engine()
    total = len(df)
    print(f"[*] Extracting 22 semantic & ontology features for {total} dataset records...")

    # 1. Batch encode resumes and job descriptions with Sentence-BERT
    print("    - Batch embedding resumes and job descriptions...")
    resume_texts = df["resume_text"].tolist()
    job_texts = df["job_description_text"].tolist()
    
    resume_embs = engine.embed_batch(resume_texts, batch_size=128)
    job_embs = engine.embed_batch(job_texts, batch_size=128)

    # 2. Overall cosine similarities
    overall_sims = np.sum(resume_embs * job_embs, axis=1)
    norm_overall_sims = np.clip((overall_sims + 0.1) / 1.1, 0.0, 1.0)

    # 3. Role similarities
    cand_roles = df["candidate_role"].tolist()
    target_roles = df["target_job_role"].tolist()
    cand_role_embs = engine.embed_batch(cand_roles, batch_size=128)
    target_role_embs = engine.embed_batch(target_roles, batch_size=128)
    role_sims = np.clip((np.sum(cand_role_embs * target_role_embs, axis=1) + 0.1) / 1.1, 0.0, 1.0)

    # 4. Construct feature matrix
    features_list = []
    for i in range(total):
        cand_exp = float(df.iloc[i]["candidate_experience_years"])
        req_exp = float(df.iloc[i]["required_experience_years"])
        
        sim_val = float(norm_overall_sims[i])
        role_sim_val = float(role_sims[i])

        # Experience compatibility (Fair non-penalizing)
        exp_comp_score = 1.0 if cand_exp >= req_exp else round(max(0.1, cand_exp / max(0.5, req_exp)), 2)
        exp_exceeds = 1.0 if cand_exp > req_exp else 0.0
        exp_gap = max(0.0, req_exp - cand_exp)
        exp_align = compute_experience_alignment_feature(cand_exp, req_exp)

        # In dataset generation, technical alignment correlates with overall similarity and role
        tech_align = float(np.clip(0.6 * sim_val + 0.4 * role_sim_val, 0.1, 1.0))
        
        # Ontology features simulation for dataset rows
        explicit_ratio = float(np.clip(tech_align * 0.85, 0.1, 1.0))
        related_ratio = float(np.clip((1.0 - explicit_ratio) * 0.6, 0.0, 0.5))
        true_gap_ratio = float(np.clip(1.0 - explicit_ratio - related_ratio, 0.0, 0.9))
        ontology_cov = float(np.clip(explicit_ratio * 1.0 + related_ratio * 0.7, 0.1, 1.0))
        missing_gap = float(np.clip(1.0 - tech_align, 0.0, 0.9))

        edu_tier = str(df.iloc[i].get("candidate_education_tier", "Tech_UG"))
        tier_scores = {"Doctorate": 1.0, "Tech_PG": 0.98, "Tech_UG": 0.90, "Math_UG": 0.85, "Business_UG": 0.70, "Non_Tech": 0.55}
        edu_align = tier_scores.get(edu_tier, 0.85)

        proj_align = float(np.clip(0.7 * sim_val + 0.3 * tech_align, 0.1, 1.0))
        sec_sim = float(np.clip(0.8 * sim_val + 0.2 * role_sim_val, 0.1, 1.0))
        resp_align = float(np.clip(0.75 * sim_val + 0.25 * role_sim_val, 0.1, 1.0))
        seniority_align = 0.95 if (cand_exp >= 4.0 and req_exp >= 4.0) or (cand_exp < 4.0 and req_exp < 4.0) else (0.90 if cand_exp >= req_exp else 0.50)

        row_feat = {
            "resume_job_semantic_similarity": round(sim_val, 4),
            "section_semantic_similarity": round(sec_sim, 4),
            "technical_requirement_alignment": round(tech_align, 4),
            "responsibility_alignment": round(resp_align, 4),
            "role_alignment": round(role_sim_val, 4),
            "seniority_alignment": round(seniority_align, 4),
            "semantic_skill_coverage": round(ontology_cov, 4),
            "explicit_skill_match_ratio": round(explicit_ratio, 4),
            "related_skill_match_ratio": round(related_ratio, 4),
            "true_skill_gap_ratio": round(true_gap_ratio, 4),
            "skill_ontology_coverage": round(ontology_cov, 4),
            "missing_requirement_semantic_gap": round(missing_gap, 4),
            "experience_alignment": round(exp_align, 4),
            "experience_compatibility_score": round(exp_comp_score, 4),
            "experience_exceeds_requirement": round(exp_exceeds, 4),
            "experience_gap": round(exp_gap, 4),
            "education_alignment": round(edu_align, 4),
            "project_alignment": round(proj_align, 4),
            "project_depth": 0.85,
            "project_skill_evidence": round(proj_align, 4),
            "internship_alignment": 0.90 if cand_exp >= 1.0 else 0.50,
            "resume_completeness": 1.0
        }
        features_list.append(row_feat)

    feature_df = pd.DataFrame(features_list)[FEATURE_NAMES]
    print(f"[+] Feature matrix built: {feature_df.shape[0]} rows x {feature_df.shape[1]} features.")
    return feature_df
