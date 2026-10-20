"""
Education Extractor for CareerMatch AI.
Extracts degree level, major/field, institution, and graduation year.
Returns 'Not clearly specified' when information is absent.
"""

import re
from typing import Dict, Any, List


DEGREE_PATTERNS = [
    (r"\b(Ph\.?D|Doctor of Philosophy)\b", "Doctorate", "Ph.D."),
    (r"\b(M\.?Tech|Master of Technology)\b", "Master", "M.Tech"),
    (r"\b(M\.?S\.?|Master of Science)\b", "Master", "M.S."),
    (r"\b(M\.?C\.?A\.?|Master of Computer Applications)\b", "Master", "M.C.A."),
    (r"\b(M\.?B\.?A\.?|Master of Business Administration)\b", "Master", "M.B.A."),
    (r"\b(B\.?Tech|Bachelor of Technology)\b", "Bachelor", "B.Tech"),
    (r"\b(B\.?E\.?|Bachelor of Engineering)\b", "Bachelor", "B.E."),
    (r"\b(B\.?S\.?|Bachelor of Science)\b", "Bachelor", "B.S."),
    (r"\b(B\.?C\.?A\.?|Bachelor of Computer Applications)\b", "Bachelor", "B.C.A."),
    (r"\b(B\.?B\.?A\.?|Bachelor of Business Administration)\b", "Bachelor", "B.B.A."),
    (r"\b(Bachelor(?:'s)? Degree)\b", "Bachelor", "Bachelor's Degree")
]

FIELD_PATTERNS = [
    (r"\b(?:computer science(?: and engineering)?|cse)\b", "Computer Science & Engineering"),
    (r"\b(?:artificial intelligence(?: and data science)?|ai(?: &| and)? ds|ai)\b", "Artificial Intelligence & Data Science"),
    (r"\b(?:data science(?: and analytics)?)\b", "Data Science"),
    (r"\b(?:information technology|it)\b", "Information Technology"),
    (r"\b(?:mathematics and computing|statistics|applied mathematics)\b", "Mathematics & Statistics"),
    (r"\b(?:electronics and communication(?: engineering)?|ece)\b", "Electronics & Communication"),
    (r"\b(?:electrical engineering|ee)\b", "Electrical Engineering"),
    (r"\b(?:mechanical engineering)\b", "Mechanical Engineering"),
    (r"\b(?:business analytics)\b", "Business Analytics")
]

INSTITUTION_KEYWORDS = [
    r"\b([A-Z][A-Za-z\s&]+(?:Institute of Technology|University|College|IIT|NIT|BITS|IIIT|Academy))\b",
    r"\b(IIT\s+[A-Za-z]+|NIT\s+[A-Za-z]+|BITS\s+[A-Za-z]+)\b"
]


def extract_education_details(text: str, education_section_text: str = "") -> Dict[str, Any]:
    """
    Extracts degree, major, institution, and graduation year from resume text.
    """
    search_text = education_section_text if education_section_text.strip() else text

    # 1. Degree identification
    detected_degree = None
    detected_tier = "Other"
    for pattern, tier, label in DEGREE_PATTERNS:
        if re.search(pattern, search_text, re.IGNORECASE):
            detected_degree = label
            detected_tier = tier
            break

    # 2. Field / Major identification
    detected_field = None
    for pattern, label in FIELD_PATTERNS:
        if re.search(pattern, search_text, re.IGNORECASE):
            detected_field = label
            break

    # 3. Graduation Year
    # Look for 4 digit year between 1990 and 2030
    grad_year = None
    year_matches = re.findall(r"\b(199\d|20[0-2]\d|2030)\b", search_text)
    if year_matches:
        # Pick the most recent year as graduation/anticipated graduation
        grad_year = max([int(y) for y in year_matches])

    # 4. Institution identification
    detected_institution = None
    for inst_pat in INSTITUTION_KEYWORDS:
        inst_match = re.search(inst_pat, search_text)
        if inst_match:
            candidate_inst = inst_match.group(1).strip()
            if 3 < len(candidate_inst) < 60:
                detected_institution = candidate_inst
                break

    degree_display = f"{detected_degree} in {detected_field}" if detected_degree and detected_field else (detected_degree or detected_field or "Not clearly specified")
    institution_display = detected_institution or "Not clearly specified"
    year_display = str(grad_year) if grad_year else "Not clearly specified"

    return {
        "degree": detected_degree or "Not clearly specified",
        "tier": detected_tier,
        "field": detected_field or "Not clearly specified",
        "institution": institution_display,
        "graduation_year": year_display,
        "education_display": degree_display,
        "is_specified": detected_degree is not None or detected_field is not None
    }
