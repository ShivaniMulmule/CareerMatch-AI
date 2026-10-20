"""
Actionable Recommendation Engine for CareerMatch AI.
Translates detected semantic skill gaps into targeted portfolio projects,
specific bridge courses, certification paths, and resume bullet optimizations.
"""

import json
import os
from typing import Dict, Any, List
import numpy as np

from ml.embeddings import get_embedding_engine


def load_learning_resources() -> Dict[str, Any]:
    path = os.path.join("data", "learning_resources.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"resources": [], "general_advice": []}


def generate_recommendations(
    skill_gap_results: Dict[str, Any],
    match_score: float,
    dimension_scores: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Synthesizes actionable recommendations tailored directly to detected gaps.
    """
    engine = get_embedding_engine()
    catalog = load_learning_resources()
    resources_list = catalog.get("resources", [])
    general_advice = catalog.get("general_advice", [])

    gaps = skill_gap_results.get("skill_gaps", [])
    partial = skill_gap_results.get("partial_requirements", [])
    all_deficiencies = gaps + partial

    if not all_deficiencies:
        # Candidate is exceptionally well matched
        return {
            "summary": "Outstanding profile alignment! Minor optimizations recommended for senior competitive edge.",
            "recommended_projects": [
                {
                    "title": "Production System Optimization & Benchmark Whitepaper",
                    "description": "Publish a reproducible benchmark analyzing latency, throughput, and memory profiling of your deployed architectures.",
                    "target_gap": "Advanced System Optimization"
                }
            ],
            "recommended_courses": [],
            "certifications": ["AWS Certified Solutions Architect", "Google Cloud Professional ML Engineer"],
            "resume_enhancements": [
                "Quantify business outcomes: state dollar savings, latency decreases, or model accuracy gains.",
                "Highlight mentorship, team leadership, or open-source community contributions."
            ]
        }

    # Match deficiencies to resource catalog via semantic vector embedding
    resource_skills = [r["skill"] for r in resources_list]
    matched_projects = []
    matched_courses = []
    matched_certs = set()
    resume_tips = []

    if resource_skills:
        skill_embeddings = engine.embed_batch(resource_skills)
        deficiency_embeddings = engine.embed_batch(all_deficiencies[:5])
        sim_matrix = engine.batch_cosine_similarity(deficiency_embeddings, skill_embeddings)

        used_skills = set()
        for i, def_text in enumerate(all_deficiencies[:5]):
            best_j = int(np.argmax(sim_matrix[i]))
            best_sim = float(sim_matrix[i][best_j])
            matched_skill_name = resource_skills[best_j]

            if matched_skill_name not in used_skills and best_sim > 0.35:
                used_skills.add(matched_skill_name)
                res_item = resources_list[best_j]

                # Add projects
                for p in res_item.get("recommended_projects", [])[:1]:
                    matched_projects.append({
                        "title": p["title"],
                        "description": p["description"],
                        "target_gap": def_text[:100]
                    })

                # Add courses
                for c in res_item.get("courses", [])[:1]:
                    matched_courses.append({
                        "title": c["title"],
                        "provider": c["provider"],
                        "level": c["level"],
                        "url": c.get("url", "#"),
                        "closes_gap": def_text[:80]
                    })

                # Add certifications
                for cert in res_item.get("certifications", []):
                    matched_certs.add(cert)

                # Add resume advice
                if res_item.get("resume_advice"):
                    resume_tips.append(res_item["resume_advice"])

    # Fallback if catalog matching didn't yield enough
    if not matched_projects:
        for gap in all_deficiencies[:2]:
            matched_projects.append({
                "title": f"Hands-On Implementation: {gap[:50]}",
                "description": f"Design and implement an end-to-end prototype specifically demonstrating practical competency in '{gap[:80]}'. Deploy it to GitHub with clear README documentation and automated test suites.",
                "target_gap": gap[:100]
            })

    # Dimension-specific coaching
    coaching_summary = []
    if dimension_scores:
        if dimension_scores.get("project_alignment", 100) < 65:
            coaching_summary.append("Your projects should more directly mirror the production duties described in the target job.")
        if dimension_scores.get("experience_alignment", 100) < 60:
            coaching_summary.append("There is a seniority duration gap; compensate by demonstrating high project complexity and architectural ownership.")
        if dimension_scores.get("capability_alignment", 100) < 65:
            coaching_summary.append("Target the unverified core capabilities highlighted in the Skill Gap Matrix below.")

    summary_text = " ".join(coaching_summary) if coaching_summary else "Actionable roadmap designed to address the highest-impact qualification gaps."

    return {
        "summary": summary_text,
        "recommended_projects": matched_projects[:3],
        "recommended_courses": matched_courses[:3],
        "certifications": list(matched_certs)[:4],
        "resume_enhancements": (resume_tips + general_advice)[:4]
    }
