"""
Experience Extractor & Compatibility Engine for CareerMatch AI.
Extracts professional experience, internships, leadership roles, research, and project tenure.
Features a dedicated, fair experience compatibility evaluator:
  - Having MORE experience than required is NEVER penalized.
  - Distinguishes exact matches, exceedances, partials, gaps, and freshers-friendly postings.
"""

import re
from typing import Dict, Any, List, Optional, Tuple


def parse_jd_experience_requirements(jd_text: str) -> Dict[str, Any]:
    """
    Parses job description to extract experience constraints:
    min_years, max_years, is_freshers_welcome, is_required, is_preferred.
    """
    lower_jd = jd_text.lower()

    # 1. Check for explicit freshers / no experience indicators
    freshers_patterns = [
        r"\b(?:no\s+experience\s+required|no\s+prior\s+experience|0\s+years?(?:\s+of)?\s+experience)\b",
        r"\b(?:freshers?\s+welcome|freshers?\s+can\s+apply|entry\s*[-]?\s*level|open\s+to\s+freshers?)\b",
        r"\b(?:0\s*[-to]+\s*0\s*years?)\b"
    ]
    for pat in freshers_patterns:
        if re.search(pat, lower_jd):
            return {
                "min_years": 0.0,
                "max_years": None,
                "is_freshers_welcome": True,
                "is_specified": True,
                "is_required": True,
                "is_preferred": False,
                "raw_match": "No experience required / Freshers welcome"
            }

    # 2. Check for range mentions: e.g. "0-1 years", "0 to 2 years", "1-3 years", "2-5 yrs"
    range_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
        lower_jd
    )
    if range_match:
        min_y = float(range_match.group(1))
        max_y = float(range_match.group(2))
        return {
            "min_years": min_y,
            "max_years": max_y,
            "is_freshers_welcome": min_y == 0.0,
            "is_specified": True,
            "is_required": True,
            "is_preferred": "prefer" in lower_jd or "nice to have" in lower_jd,
            "raw_match": f"{min_y}-{max_y} years"
        }

    # 3. Check for minimum mentions: e.g. "minimum 2 years", "at least 3 years", "2+ years", "3+ yrs"
    min_match = re.search(
        r"(?:minimum|at\s+least|min\.?)\s*(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)",
        lower_jd
    )
    if min_match:
        min_y = float(min_match.group(1))
        return {
            "min_years": min_y,
            "max_years": None,
            "is_freshers_welcome": min_y == 0.0,
            "is_specified": True,
            "is_required": True,
            "is_preferred": False,
            "raw_match": f"Minimum {min_y} years"
        }

    # 4. Check for plus mentions: e.g. "3+ years of experience"
    plus_match = re.search(
        r"(\d+(?:\.\d+)?)\s*\+\s*(?:years?|yrs?)(?:\s+of\s+experience)?",
        lower_jd
    )
    if plus_match:
        min_y = float(plus_match.group(1))
        return {
            "min_years": min_y,
            "max_years": None,
            "is_freshers_welcome": min_y == 0.0,
            "is_specified": True,
            "is_required": True,
            "is_preferred": False,
            "raw_match": f"{min_y}+ years"
        }

    # 5. General experience mention: e.g. "2 years experience"
    gen_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)(?:\s+of)?(?:\s+(?:relevant|hands-on|industry|work))?\s+experience",
        lower_jd
    )
    if gen_match:
        min_y = float(gen_match.group(1))
        return {
            "min_years": min_y,
            "max_years": None,
            "is_freshers_welcome": min_y == 0.0,
            "is_specified": True,
            "is_required": True,
            "is_preferred": False,
            "raw_match": f"{min_y} years"
        }

    # Default fallback: experience not explicitly specified
    return {
        "min_years": 0.0,
        "max_years": None,
        "is_freshers_welcome": True,
        "is_specified": False,
        "is_required": False,
        "is_preferred": False,
        "raw_match": "Not explicitly specified"
    }


def experience_compatibility(
    candidate_experience: float,
    jd_min_experience: Optional[float] = 0.0,
    jd_max_experience: Optional[float] = None,
    experience_required: bool = True,
    experience_preferred: bool = False,
    is_strict_maximum: bool = False,
    is_freshers_welcome: bool = False
) -> Dict[str, Any]:
    """
    Dedicated Experience Compatibility Function.
    Evaluates candidate tenure against JD criteria.
    Guarantees:
      - Having MORE experience than minimum required is NEVER penalized.
      - Distinguishes: MATCH, STRONG MATCH, PARTIAL MATCH, EXPERIENCE GAP,
        EXCEEDS PREFERRED RANGE, NOT SPECIFIED.
      - Returns continuous calibrated compatibility score [0.0, 1.0].
    """
    cand = max(0.0, float(candidate_experience))
    min_req = 0.0 if jd_min_experience is None else max(0.0, float(jd_min_experience))
    max_req = None if jd_max_experience is None else max(0.0, float(jd_max_experience))

    # Case 1: Freshers welcome or no experience required
    if is_freshers_welcome or min_req == 0.0:
        if max_req is not None and cand > max_req:
            # e.g. JD: 0-1 years, candidate: 3 years
            return {
                "status": "EXCEEDS PREFERRED RANGE",
                "score": 0.95,
                "reason": (
                    f"Job welcomes freshers / entry-level ({min_req:.0f}-{max_req:.0f} years preferred). "
                    f"Candidate has {cand:.1f} years of relevant experience. Exceeds preferred range "
                    f"without negative penalty (potential overqualification, not an experience gap)."
                ),
                "candidate_years": cand,
                "jd_min_years": min_req,
                "jd_max_years": max_req,
                "exceeds": True,
                "is_gap": False
            }
        else:
            return {
                "status": "MATCH",
                "score": 1.0,
                "reason": (
                    f"Job welcomes freshers / has no minimum experience requirement. "
                    f"Candidate satisfies criteria with {cand:.1f} years of experience."
                ),
                "candidate_years": cand,
                "jd_min_years": min_req,
                "jd_max_years": max_req,
                "exceeds": False,
                "is_gap": False
            }

    # Case 2: Candidate meets or exceeds minimum requirement
    if cand >= min_req:
        # Check if exceeds preferred upper bound
        if max_req is not None and cand > max_req:
            if is_strict_maximum:
                return {
                    "status": "EXCEEDS PREFERRED RANGE",
                    "score": 0.85,
                    "reason": (
                        f"Candidate experience ({cand:.1f} years) exceeds the stated upper limit "
                        f"({max_req:.1f} years). Potential overqualification for entry-band leveling."
                    ),
                    "candidate_years": cand,
                    "jd_min_years": min_req,
                    "jd_max_years": max_req,
                    "exceeds": True,
                    "is_gap": False
                }
            else:
                return {
                    "status": "EXCEEDS PREFERRED RANGE",
                    "score": 1.0,
                    "reason": (
                        f"Candidate has {cand:.1f} years experience, which exceeds the preferred range "
                        f"({min_req:.0f}-{max_req:.0f} years). More experience is positive and broadens "
                        f"technical execution depth."
                    ),
                    "candidate_years": cand,
                    "jd_min_years": min_req,
                    "jd_max_years": max_req,
                    "exceeds": True,
                    "is_gap": False
                }
        else:
            # Meets range or minimum requirement cleanly
            is_strong = cand >= (min_req + 1.0)
            return {
                "status": "STRONG MATCH" if is_strong else "MATCH",
                "score": 1.0,
                "reason": (
                    f"Candidate has {cand:.1f} years experience, successfully meeting the required "
                    f"threshold of {min_req:.1f} years."
                ),
                "candidate_years": cand,
                "jd_min_years": min_req,
                "jd_max_years": max_req,
                "exceeds": False,
                "is_gap": False
            }

    # Case 3: Candidate has less experience than minimum
    deficit = min_req - cand
    ratio = cand / max(0.5, min_req)

    if experience_preferred and not experience_required:
        return {
            "status": "PARTIAL MATCH",
            "score": round(max(0.65, ratio), 2),
            "reason": (
                f"Experience of {min_req:.1f} years is preferred but not strictly required. "
                f"Candidate brings {cand:.1f} years of relevant background."
            ),
            "candidate_years": cand,
            "jd_min_years": min_req,
            "jd_max_years": max_req,
            "exceeds": False,
            "is_gap": False
        }
    elif ratio >= 0.70:
        return {
            "status": "PARTIAL MATCH",
            "score": round(max(0.40, ratio), 2),
            "reason": (
                f"Candidate has {cand:.1f} years of experience, approaching the required "
                f"{min_req:.1f} years (deficit of {deficit:.1f} years)."
            ),
            "candidate_years": cand,
            "jd_min_years": min_req,
            "jd_max_years": max_req,
            "exceeds": False,
            "is_gap": True
        }
    else:
        return {
            "status": "EXPERIENCE GAP",
            "score": round(max(0.10, ratio), 2),
            "reason": (
                f"Candidate has {cand:.1f} years of experience, but job requires a minimum "
                f"of {min_req:.1f} years (deficit of {deficit:.1f} years)."
            ),
            "candidate_years": cand,
            "jd_min_years": min_req,
            "jd_max_years": max_req,
            "exceeds": False,
            "is_gap": True
        }


def extract_experience_details(
    text: str,
    experience_section_text: str = "",
    project_section_text: str = ""
) -> Dict[str, Any]:
    """
    Extracts multi-faceted experience details:
      - professional_experience_years (industry/employment tenure)
      - internship_experience_years (internships)
      - project_experience_years (academic & portfolio projects)
      - research_experience_years (publications & lab research)
      - total_years_num (aggregate professional seniority)
    """
    combined_exp_text = experience_section_text if experience_section_text.strip() else text
    lower_text = text.lower()
    
    # 1. Total Industry Experience Duration Estimation
    extracted_years: List[float] = []

    # Direct mention scan (e.g. "4 years of experience", "3.5 yrs")
    for match in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:\+|-\d+)?\s*(?:years?|yrs?)\b", text, re.IGNORECASE):
        try:
            val = float(match.group(1))
            if 0.2 <= val <= 40.0:
                extracted_years.append(val)
        except ValueError:
            pass

    # Date range scan across employment lines
    date_ranges = re.findall(
        r"\b(20\d{2}|19\d{2})\b\s*(?:-|to)\s*\b(20\d{2}|present|current)\b",
        combined_exp_text,
        re.IGNORECASE
    )
    current_year = 2026
    date_span_years = 0.0

    for start_str, end_str in date_ranges:
        try:
            start_yr = int(start_str)
            end_yr = current_year if end_str.lower() in ["present", "current"] else int(end_str)
            span = max(0, end_yr - start_yr)
            if 0 < span <= 30:
                date_span_years += span
        except Exception:
            continue

    if extracted_years:
        total_years = max(extracted_years)
    elif date_span_years > 0:
        total_years = min(date_span_years, 25.0)
    else:
        # Check if candidate mentions fresher or student
        if re.search(r"\b(fresher|graduate|student|entry-level)\b", lower_text):
            total_years = 0.0
        else:
            total_years = None

    # 2. Extract Internships & Internship Duration
    internships = []
    intern_matches = re.finditer(r"([^\n\.]*(?:intern|internship)[^\n\.]*)", combined_exp_text, re.IGNORECASE)
    for m in intern_matches:
        snip = m.group(1).strip()
        if len(snip) > 10 and snip not in internships:
            internships.append(snip[:120])

    internship_years = 0.0
    if internships:
        # Estimate ~0.3 - 0.5 years per distinct internship mentioned
        internship_years = round(min(2.0, len(internships) * 0.4), 1)

    # 3. Extract Research & Academic Experience
    research_mentions = []
    research_matches = re.finditer(r"([^\n\.]*(?:research|publication|paper|conference|thesis|lab)[^\n\.]*)", text, re.IGNORECASE)
    for m in research_matches:
        snip = m.group(1).strip()
        if len(snip) > 15 and snip not in research_mentions:
            research_mentions.append(snip[:120])
    research_years = round(min(3.0, len(research_mentions) * 0.5), 1) if research_mentions else 0.0

    # 4. Project Experience Estimation
    proj_text = project_section_text if project_section_text.strip() else text
    proj_blocks = re.findall(r"(?:project|capstone|system|application|platform)[\s\w]*:", proj_text, re.IGNORECASE)
    project_years = round(min(2.5, max(0.5, len(proj_blocks) * 0.4)), 1) if proj_blocks else 0.5

    # 5. Extract Leadership Mentions
    leadership_indicators = []
    lead_matches = re.finditer(r"([^\n\.]*(?:lead|led|managed|headed|mentored|architected)[^\n\.]*)", combined_exp_text, re.IGNORECASE)
    for m in lead_matches:
        snip = m.group(1).strip()
        if len(snip) > 15 and snip not in leadership_indicators:
            leadership_indicators.append(snip[:120])

    # 6. Identified Roles & Titles
    role_titles = []
    common_titles = [
        "Machine Learning Engineer", "Data Scientist", "Data Analyst", "AI Engineer",
        "NLP Engineer", "Computer Vision Engineer", "Software Engineer", "Backend Developer",
        "Frontend Developer", "Data Engineer", "Cloud Engineer", "DevOps Engineer",
        "Full Stack Developer", "Research Intern", "Software Developer"
    ]
    for title in common_titles:
        if re.search(rf"\b{re.escape(title)}\b", text, re.IGNORECASE):
            role_titles.append(title)

    primary_years = total_years if total_years is not None else (internship_years if internship_years > 0 else 0.0)
    years_str = f"{primary_years:.1f} years" if total_years is not None else "Not clearly specified"

    return {
        "total_years_num": primary_years,
        "professional_experience_years": primary_years,
        "internship_experience_years": internship_years,
        "project_experience_years": project_years,
        "research_experience_years": research_years,
        "total_years_display": years_str,
        "is_specified": total_years is not None,
        "detected_titles": role_titles[:5],
        "internships": internships[:3],
        "has_internships": len(internships) > 0,
        "leadership_highlights": leadership_indicators[:3],
        "has_leadership": len(leadership_indicators) > 0,
        "research_highlights": research_mentions[:3],
        "has_research": len(research_mentions) > 0,
        "experience_section_present": bool(experience_section_text.strip())
    }
