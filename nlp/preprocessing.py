"""
Text Preprocessing and Section Segmentation for CareerMatch AI.
Segments resume and job description texts into structural sections and sentences.
"""

import re
from typing import Dict, List, Any


SECTION_HEADERS = {
    "summary": [
        "summary", "professional summary", "profile", "about me", "executive summary",
        "career objective", "objective", "biography"
    ],
    "experience": [
        "experience", "work experience", "professional experience", "employment history",
        "work history", "career history", "internships", "relevant experience"
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "technologies", "skill set",
        "technical competencies", "areas of expertise", "tools & technologies", "capabilities"
    ],
    "projects": [
        "projects", "academic projects", "key projects", "personal projects",
        "technical projects", "portfolio", "capstone projects"
    ],
    "education": [
        "education", "academic background", "qualifications", "academic qualifications",
        "educational background", "degrees"
    ],
    "certifications": [
        "certifications", "licenses", "certificates", "courses & certifications",
        "professional certifications", "accreditations"
    ]
}


def clean_text(text: str) -> str:
    """Normalize whitespace, remove non-printable control characters, and clean up bullets."""
    if not text:
        return ""
    # Replace common bullet characters with standard dash
    text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25AB]", "\n- ", text)
    # Replace non-breaking spaces
    text = text.replace("\xa0", " ")
    # Replace tabs with spaces
    text = text.replace("\t", " ")
    # Reduce multi-line carriage returns
    text = re.sub(r"\r\n|\r", "\n", text)
    # Reduce multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Reduce multiple spaces
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def segment_sentences(text: str) -> List[str]:
    """
    Split text into granular candidate evidence sentences.
    Preserves bullet points as individual units.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []

    lines = cleaned.split("\n")
    sentences = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # If line starts with a bullet dash or number
        if line.startswith("-") or line.startswith("*") or re.match(r"^\d+[\.\)]", line):
            content = re.sub(r"^[-*\d\.\)\s]+", "", line).strip()
            if len(content) > 15:
                sentences.append(content)
        else:
            # Split sentences by period/semicolon followed by space and capital or newline
            sub_sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", line)
            for s in sub_sentences:
                s_clean = s.strip()
                if len(s_clean) > 15:
                    sentences.append(s_clean)

    return sentences


def segment_sections(text: str) -> Dict[str, str]:
    """
    Parses resume or job description text into standard logical sections.
    Returns a dictionary mapping section keys to section text content.
    """
    cleaned = clean_text(text)
    lines = cleaned.split("\n")

    sections: Dict[str, List[str]] = {
        "summary": [],
        "experience": [],
        "skills": [],
        "projects": [],
        "education": [],
        "certifications": [],
        "other": []
    }

    current_section = "summary"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if line resembles a section header
        # Usually short (< 40 chars) and matches known aliases
        header_candidate = stripped.lower().rstrip(":-")
        matched_section = None

        if len(stripped) < 45:
            for sec_key, aliases in SECTION_HEADERS.items():
                for alias in aliases:
                    if header_candidate == alias or header_candidate == f"{alias}:":
                        matched_section = sec_key
                        break
                if matched_section:
                    break

        if matched_section:
            current_section = matched_section
        else:
            sections[current_section].append(stripped)

    # Convert list of lines into cohesive text blocks
    return {sec: "\n".join(content_lines).strip() for sec, content_lines in sections.items()}
