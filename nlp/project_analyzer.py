"""
Project Analyzer for CareerMatch AI.
Identifies project descriptions semantically, embeds them with Sentence-BERT,
and compares them against job responsibilities via cosine similarity.
Zero keyword counting - true vector semantic understanding.
"""

import re
from typing import Dict, Any, List
import numpy as np
from ml.embeddings import get_embedding_engine


def extract_project_blocks(project_text: str, full_resume_text: str) -> List[Dict[str, str]]:
    """
    Splits projects section or full resume text into individual project blocks.
    """
    target_text = project_text if project_text.strip() else full_resume_text
    lines = [l.strip() for l in target_text.split("\n") if l.strip()]

    projects = []
    current_title = ""
    current_body = []

    for line in lines:
        # Detect project title line (e.g. starts with dash, bullet, or bold-like title with colon)
        is_title = False
        if line.startswith("-") or line.startswith("*"):
            # Check if line has a title separator like ':' or '|'
            if ":" in line[:45] or "|" in line[:45]:
                is_title = True
        elif len(line) < 60 and (line.isupper() or line.endswith(":") or "|" in line):
            is_title = True

        if is_title and current_body:
            projects.append({
                "title": current_title or "Project",
                "description": " ".join(current_body)
            })
            current_title = line.lstrip("-* ").rstrip(":")
            current_body = []
        elif is_title and not current_body:
            current_title = line.lstrip("-* ").rstrip(":")
        else:
            current_body.append(line.lstrip("-* "))

    if current_body:
        projects.append({
            "title": current_title or "Technical Project",
            "description": " ".join(current_body)
        })

    # If parsing yields 0 projects but projects section had content
    if not projects and len(target_text) > 30:
        projects.append({
            "title": "Demonstrated Technical Projects",
            "description": target_text[:500]
        })

    return projects[:6]


def analyze_projects_semantic(
    projects_list: List[Dict[str, str]],
    job_description_text: str,
    job_responsibilities_text: str = ""
) -> Dict[str, Any]:
    """
    Compares project descriptions to job responsibilities and overall JD
    using dense vector embeddings and cosine similarity.
    """
    engine = get_embedding_engine()

    benchmark_text = job_responsibilities_text if job_responsibilities_text.strip() else job_description_text
    if not benchmark_text.strip():
        benchmark_text = "Software engineering, machine learning modeling, backend development, and architecture."

    benchmark_embedding = engine.embed_text(benchmark_text)

    if not projects_list:
        return {
            "project_count": 0,
            "overall_project_relevance": 0.20,
            "project_relevance_pct": 20.0,
            "evaluated_projects": [],
            "top_relevant_project": None,
            "explanation": "No distinct project section was identified in the resume."
        }

    evaluated_projects = []
    similarities = []

    for proj in projects_list:
        title = proj.get("title", "Project")
        desc = proj.get("description", "")
        combined_proj_text = f"{title}: {desc}"
        proj_emb = engine.embed_text(combined_proj_text)
        sim = engine.cosine_similarity(proj_emb, benchmark_embedding)
        # Normalize cosine similarity [-1, 1] to positive alignment score [0, 1]
        sim_norm = float(np.clip((sim + 0.2) / 1.2, 0.0, 1.0))
        similarities.append(sim_norm)

        evaluated_projects.append({
            "title": title,
            "description_snippet": desc[:250] + ("..." if len(desc) > 250 else ""),
            "semantic_similarity": round(sim, 3),
            "relevance_score": round(sim_norm * 100, 1),
            "alignment_tier": "High" if sim_norm >= 0.70 else ("Moderate" if sim_norm >= 0.45 else "Low")
        })

    # Sort evaluated projects by relevance
    evaluated_projects.sort(key=lambda x: x["relevance_score"], reverse=True)
    avg_relevance = float(np.mean(similarities)) if similarities else 0.20
    top_relevance = float(np.max(similarities)) if similarities else 0.20
    
    # Blended project score: 60% top project relevance + 40% average
    blended_relevance = float(np.clip(0.6 * top_relevance + 0.4 * avg_relevance, 0.10, 0.98))

    return {
        "project_count": len(evaluated_projects),
        "overall_project_relevance": round(blended_relevance, 3),
        "project_relevance_pct": round(blended_relevance * 100, 1),
        "evaluated_projects": evaluated_projects,
        "top_relevant_project": evaluated_projects[0] if evaluated_projects else None,
        "explanation": f"Evaluated {len(evaluated_projects)} candidate projects against job responsibilities via S-BERT embeddings."
    }
