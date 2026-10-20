"""
Unit tests for NLP extractors and text preprocessing in CareerMatch AI.
"""

import pytest
from nlp.preprocessing import clean_text, segment_sentences, segment_sections
from nlp.experience_extractor import extract_experience_details
from nlp.education_extractor import extract_education_details
from nlp.pdf_reader import validate_pdf_bytes, PDFProcessingError


def test_clean_text_and_segment_sentences():
    raw_sample = "• Built predictive model in Python.\n• Deployed API using FastAPI on AWS."
    cleaned = clean_text(raw_sample)
    sentences = segment_sentences(cleaned)
    assert len(sentences) >= 2
    assert "FastAPI" in sentences[1]


def test_experience_extractor_detection():
    sample_text = """
    EXPERIENCE:
    Software Engineer at TechCorp (2020 - 2024).
    Developed high throughput microservices.
    Completed 6-month machine learning internship at DataFlow Labs.
    Led sprint planning and architectural reviews.
    """
    res = extract_experience_details(sample_text)
    assert res["is_specified"] is True
    assert res["total_years_num"] >= 3.5
    assert res["has_internships"] is True
    assert res["has_leadership"] is True


def test_education_extractor_detection():
    sample_text = """
    EDUCATION:
    B.Tech in Computer Science & Engineering, IIT Bombay (Graduated 2023)
    """
    edu = extract_education_details(sample_text)
    assert edu["degree"] == "B.Tech"
    assert "Computer Science" in edu["field"]
    assert edu["graduation_year"] == "2023"


def test_pdf_reader_security_checks():
    # Empty bytes check
    with pytest.raises(PDFProcessingError):
        validate_pdf_bytes(b"")

    # Invalid header check
    with pytest.raises(PDFProcessingError):
        validate_pdf_bytes(b"NOT_A_PDF_FILE_HEADER")
