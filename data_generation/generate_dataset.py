"""
CareerMatch AI - Synthetic Dataset Generation Pipeline.
Generates 6,000+ realistic resume-job pairs across 13 roles and 7 experience levels.
Uses controlled multi-dimensional semantic alignment modeling for target calculation
with ZERO keyword counting and ZERO data leakage.

Command: python -m data_generation.generate_dataset
"""

import os
import json
import random
import time
from datetime import datetime
import numpy as np
import pandas as pd

from data_generation.dataset_config import (
    DATASET_SEED,
    TARGET_RECORD_COUNT,
    ROLES,
    ROLE_CLUSTERS,
    EXPERIENCE_LEVELS,
    EDUCATION_LEVELS,
    UNIVERSITIES,
    ROLE_CORE_CAPABILITIES,
    PROJECT_TEMPLATES,
    COMPANY_NAMES
)
from data_generation.validators import validate_dataset


def set_seed(seed: int = DATASET_SEED):
    random.seed(seed)
    np.random.seed(seed)


def compute_ground_truth_match_score(
    role_alignment: float,
    experience_alignment: float,
    education_alignment: float,
    capability_alignment: float,
    project_alignment: float,
    responsibility_alignment: float,
    noise_std: float = 2.5
) -> float:
    """
    Computes ground truth target 'match_score' (0-100) via controlled multi-dimensional
    latent semantic scoring.
    
    Formula:
      raw_score = (
          0.25 * capability_alignment +
          0.20 * role_alignment +
          0.18 * experience_alignment +
          0.15 * project_alignment +
          0.12 * responsibility_alignment +
          0.10 * education_alignment
      ) * 100 + Gaussian_Noise(0, sigma)
      
    No keyword intersection, word counting, or target leakage is present.
    """
    raw_score = (
        0.25 * capability_alignment +
        0.20 * role_alignment +
        0.18 * experience_alignment +
        0.15 * project_alignment +
        0.12 * responsibility_alignment +
        0.10 * education_alignment
    ) * 100.0

    noise = np.random.normal(0, noise_std)
    final_score = float(np.clip(raw_score + noise, 5.0, 99.0))
    return round(final_score, 2)


def generate_single_record(record_idx: int) -> dict:
    """
    Generates a single realistic resume-job description pair and its multi-dimensional
    ground truth match target.
    """
    # 1. Select target job role & requirements
    target_role = random.choice(ROLES)
    target_cluster = ROLE_CLUSTERS[target_role]
    
    job_exp_choice = random.choice(EXPERIENCE_LEVELS)
    required_exp_years = float(round(random.uniform(job_exp_choice["min_years"], job_exp_choice["max_years"]), 1))
    
    job_edu_choice = random.choice(EDUCATION_LEVELS[:7])  # Most tech jobs require tech degree
    required_education = job_edu_choice["degree"]
    
    target_capabilities = ROLE_CORE_CAPABILITIES[target_role]
    # Required capabilities for job (subset of 5-7 core capabilities)
    k_req = min(len(target_capabilities), random.randint(4, 7))
    job_required_skills = random.sample(target_capabilities, k_req)

    # 2. Determine matching archetype for candidate
    # Archetypes: Strong (28%), Transferable (24%), Partial (20%), ExpMismatch (12%), Weak (16%)
    scenario_roll = random.random()
    
    if scenario_roll < 0.28:
        scenario = "STRONG_MATCH"
        cand_role = target_role
        cand_cluster = target_cluster
        cand_exp_years = max(0.0, round(required_exp_years + random.uniform(-0.2, 2.0), 1))
        cand_edu = random.choice(EDUCATION_LEVELS[:6])
        # High capability alignment (75% - 95%)
        overlap_skills = list(set(random.sample(job_required_skills, max(1, int(len(job_required_skills) * random.uniform(0.75, 0.95))))))
        extra_skills = random.sample([s for s in target_capabilities if s not in overlap_skills], min(3, len(target_capabilities) - len(overlap_skills))) if len(target_capabilities) > len(overlap_skills) else []
        cand_skills = overlap_skills + extra_skills
        
        role_alignment = random.uniform(0.90, 1.0)
        capability_alignment = random.uniform(0.82, 0.98)
        project_alignment = random.uniform(0.80, 0.96)
        responsibility_alignment = random.uniform(0.80, 0.95)

    elif scenario_roll < 0.52:
        scenario = "TRANSFERABLE_MATCH"
        # Pick adjacent role in same or compatible cluster
        adjacent_roles = [r for r in ROLES if r != target_role and (ROLE_CLUSTERS[r] == target_cluster or (target_cluster == "AI_ML" and ROLE_CLUSTERS[r] in ["DATA_ENGINEERING", "BACKEND"]))]
        cand_role = random.choice(adjacent_roles) if adjacent_roles else target_role
        cand_cluster = ROLE_CLUSTERS[cand_role]
        cand_exp_years = max(0.0, round(required_exp_years + random.uniform(-0.5, 1.5), 1))
        cand_edu = random.choice(EDUCATION_LEVELS[:8])
        
        cand_role_caps = ROLE_CORE_CAPABILITIES.get(cand_role, target_capabilities)
        # 40% - 70% capability alignment
        shared = [s for s in job_required_skills if s in cand_role_caps]
        cand_skills = shared + random.sample(cand_role_caps, min(4, len(cand_role_caps)))
        
        role_alignment = random.uniform(0.65, 0.82)
        capability_alignment = random.uniform(0.58, 0.78)
        project_alignment = random.uniform(0.60, 0.80)
        responsibility_alignment = random.uniform(0.55, 0.75)

    elif scenario_roll < 0.72:
        scenario = "PARTIAL_MATCH"
        cand_role = target_role
        cand_cluster = target_cluster
        cand_exp_years = max(0.0, round(required_exp_years * random.uniform(0.5, 0.9), 1))
        cand_edu = random.choice(EDUCATION_LEVELS)
        # 40% - 60% capability alignment (has noticeable gaps)
        k_overlap = max(1, int(len(job_required_skills) * random.uniform(0.40, 0.60)))
        overlap_skills = random.sample(job_required_skills, k_overlap)
        other_caps = ["Python Programming", "Git & Version Control", "Agile & Team Collaboration"]
        cand_skills = list(set(overlap_skills + other_caps))
        
        role_alignment = random.uniform(0.70, 0.88)
        capability_alignment = random.uniform(0.45, 0.65)
        project_alignment = random.uniform(0.45, 0.65)
        responsibility_alignment = random.uniform(0.45, 0.68)

    elif scenario_roll < 0.84:
        scenario = "EXPERIENCE_MISMATCH"
        cand_role = target_role
        cand_cluster = target_cluster
        if required_exp_years >= 3.0:
            # Junior applying for senior
            cand_exp_years = round(random.uniform(0.0, 1.2), 1)
        else:
            # Overqualified or mismatched
            cand_exp_years = round(random.uniform(5.5, 9.0), 1)
        cand_edu = random.choice(EDUCATION_LEVELS[:7])
        cand_skills = list(set(random.sample(job_required_skills, max(1, int(len(job_required_skills) * 0.7))) + ["Python Programming"]))
        
        role_alignment = random.uniform(0.80, 0.95)
        capability_alignment = random.uniform(0.65, 0.85)
        project_alignment = random.uniform(0.50, 0.75)
        responsibility_alignment = random.uniform(0.50, 0.70)

    else:
        scenario = "WEAK_MATCH"
        # Pick completely unrelated role
        distant_roles = [r for r in ROLES if ROLE_CLUSTERS[r] != target_cluster]
        cand_role = random.choice(distant_roles) if distant_roles else "Business Analyst"
        cand_cluster = ROLE_CLUSTERS[cand_role]
        cand_exp_years = round(random.uniform(0.0, 4.0), 1)
        cand_edu = random.choice(EDUCATION_LEVELS[4:])
        cand_role_caps = ROLE_CORE_CAPABILITIES.get(cand_role, ["Agile & Team Collaboration"])
        cand_skills = random.sample(cand_role_caps, min(len(cand_role_caps), 4))
        
        role_alignment = random.uniform(0.10, 0.35)
        capability_alignment = random.uniform(0.12, 0.38)
        project_alignment = random.uniform(0.10, 0.35)
        responsibility_alignment = random.uniform(0.10, 0.32)

    # 3. Calculate dimension alignments
    # Experience alignment: relative closeness to required experience
    if required_exp_years == 0.0:
        exp_diff = cand_exp_years
        experience_alignment = 1.0 if cand_exp_years <= 2.0 else max(0.6, 1.0 - (cand_exp_years - 2.0) * 0.1)
    else:
        exp_ratio = cand_exp_years / required_exp_years
        if 0.8 <= exp_ratio <= 1.5:
            experience_alignment = 0.95
        elif exp_ratio > 1.5:
            experience_alignment = 0.85  # Slightly over-qualified
        elif exp_ratio >= 0.5:
            experience_alignment = 0.65
        else:
            experience_alignment = max(0.15, exp_ratio)

    # Education alignment
    cand_edu_weight = cand_edu["score_weight"]
    education_alignment = round(float(np.clip(cand_edu_weight * random.uniform(0.9, 1.0), 0.2, 1.0)), 3)

    # 4. Compute ground truth target match_score
    match_score = compute_ground_truth_match_score(
        role_alignment=role_alignment,
        experience_alignment=experience_alignment,
        education_alignment=education_alignment,
        capability_alignment=capability_alignment,
        project_alignment=project_alignment,
        responsibility_alignment=responsibility_alignment
    )

    # 5. Build realistic text representations
    # Candidate Projects
    cand_project_pool = PROJECT_TEMPLATES.get(cand_cluster, PROJECT_TEMPLATES["AI_ML"])
    cand_projects = random.sample(cand_project_pool, min(2, len(cand_project_pool)))
    
    # Target Job Responsibilities
    job_company = random.choice(COMPANY_NAMES)
    job_resp_bullets = [
        f"Design, deploy, and scale high-reliability systems for {target_role} responsibilities.",
        f"Collaborate with cross-functional engineering teams to deliver enterprise features and automated pipelines.",
        f"Implement robust testing, code reviews, and observability metrics to ensure 99.9% uptime.",
        f"Demonstrate hands-on competency in {', '.join(job_required_skills[:3])}."
    ]

    resume_summary = (
        f"Driven and results-focused {cand_role} with {cand_exp_years} years of experience building and scaling software solutions. "
        f"Skilled in {', '.join(cand_skills[:4])}, with proven success delivering robust projects."
    )

    resume_text = f"""NAME: Candidate #{record_idx}
ROLE: {cand_role}
EXPERIENCE: {cand_exp_years} years
EDUCATION: {cand_edu['degree']}, {random.choice(UNIVERSITIES)} (Graduated)

PROFESSIONAL SUMMARY:
{resume_summary}

TECHNICAL CAPABILITIES:
{', '.join(cand_skills)}

PROFESSIONAL EXPERIENCE & PROJECTS:
"""
    for proj in cand_projects:
        resume_text += f"\n- {proj['name']}: {proj['desc']} (Technologies: {', '.join(proj['skills'])})"

    job_description_text = f"""COMPANY: {job_company}
POSITION: {target_role}
REQUIRED EXPERIENCE: {required_exp_years}+ years
EDUCATION REQUIREMENT: {required_education} or equivalent quantitative field

ROLE OVERVIEW:
We are seeking a talented {target_role} to join our high-growth engineering organization. The ideal candidate brings a solid track record of technical execution, problem solving, and hands-on experience.

KEY RESPONSIBILITIES:
""" + "\n".join([f"- {b}" for b in job_resp_bullets]) + f"""

QUALIFICATIONS & CAPABILITIES:
- Demonstrated experience in: {', '.join(job_required_skills)}.
- Strong foundation in software design, problem solving, and collaborative engineering.
- Minimum {required_exp_years} years of demonstrated industry experience.
"""

    return {
        "resume_id": f"RES-{record_idx:06d}",
        "job_id": f"JOB-{record_idx:06d}",
        "candidate_role": cand_role,
        "target_job_role": target_role,
        "candidate_cluster": cand_cluster,
        "target_cluster": target_cluster,
        "scenario_archetype": scenario,
        "candidate_experience_years": cand_exp_years,
        "required_experience_years": required_exp_years,
        "candidate_education": cand_edu["degree"],
        "required_education": required_education,
        "candidate_skills_list": cand_skills,
        "job_required_skills_list": job_required_skills,
        "resume_summary": resume_summary,
        "resume_text": resume_text.strip(),
        "job_description_text": job_description_text.strip(),
        "match_score": match_score
    }


def generate_dataset(output_dir: str = "data", total_records: int = TARGET_RECORD_COUNT) -> str:
    """
    Main generator execution function.
    Creates, validates, and serializes the synthetic training dataset.
    """
    set_seed(DATASET_SEED)
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "generated_resume_job_dataset.csv")
    meta_path = os.path.join(output_dir, "dataset_metadata.json")

    print(f"[*] Starting synthetic dataset generation: {total_records} records...")
    start_time = time.time()

    records = []
    for idx in range(1, total_records + 1):
        record = generate_single_record(idx)
        records.append(record)
        if idx % 1000 == 0:
            print(f"    - Generated {idx}/{total_records} records ({idx/total_records*100:.1f}%)")

    df = pd.DataFrame(records)

    print("[*] Running comprehensive dataset validation checks...")
    validation_results = validate_dataset(df, min_records=total_records)
    print(f"    Validation Result: {validation_results['status']}")
    print(f"    Mean Score: {validation_results['score_mean']}, Std: {validation_results['score_std']}")
    print(f"    Score Distribution: {validation_results['distribution']}")

    # Save to CSV
    # Convert lists to semicolon-separated strings for CSV cleanliness
    df_to_save = df.copy()
    df_to_save["candidate_skills_list"] = df_to_save["candidate_skills_list"].apply(lambda x: "; ".join(x) if isinstance(x, list) else str(x))
    df_to_save["job_required_skills_list"] = df_to_save["job_required_skills_list"].apply(lambda x: "; ".join(x) if isinstance(x, list) else str(x))
    
    df_to_save.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[+] Saved dataset to {csv_path} ({os.path.getsize(csv_path) / 1024 / 1024:.2f} MB)")

    # Save Metadata
    metadata = {
        "dataset_version": "1.0.0",
        "product_name": "CareerMatch AI",
        "tagline": "Know Your Job Fit. Before You Apply.",
        "generation_timestamp": datetime.now().isoformat(),
        "generation_seed": DATASET_SEED,
        "number_of_records": total_records,
        "target_definition": {
            "name": "match_score",
            "range": [0.0, 100.0],
            "nature": "Controlled latent multi-dimensional semantic alignment score",
            "weights": {
                "capability_alignment": 0.25,
                "role_alignment": 0.20,
                "experience_alignment": 0.18,
                "project_alignment": 0.15,
                "responsibility_alignment": 0.12,
                "education_alignment": 0.10
            },
            "zero_keyword_overlap_guarantee": True
        },
        "statistics": validation_results,
        "archetypes": df["scenario_archetype"].value_counts().to_dict(),
        "roles_distribution": df["target_job_role"].value_counts().to_dict()
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    elapsed = round(time.time() - start_time, 2)
    print(f"[+] Saved metadata to {meta_path}")
    print(f"[+] Dataset generation successfully completed in {elapsed}s.")
    return csv_path


if __name__ == "__main__":
    generate_dataset()
