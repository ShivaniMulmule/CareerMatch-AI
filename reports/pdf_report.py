"""
Executive PDF Report Generator for CareerMatch AI.
Uses ReportLab to generate downloadable, branded evaluation dossiers including
Match Score, Dimension Breakdown, 3-Tier Skill Gap & Ontology Matrix,
Experience Compatibility analysis, SHAP explanations, and actionable roadmaps.
"""

import io
import os
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)


# CareerMatch AI Brand Color Palette
COLOR_PRIMARY = colors.HexColor("#7657B8")    # Elegant Purple
COLOR_BG_LIGHT = colors.HexColor("#FAF9FC")   # Soft Linen
COLOR_ACCENT = colors.HexColor("#EDE5F8")     # Accent Light Lavender
COLOR_GREEN = colors.HexColor("#137333")      # Strong Match Green
COLOR_BLUE = colors.HexColor("#1A73E8")       # Related Match Blue
COLOR_RED = colors.HexColor("#C04828")        # Gap Red
COLOR_TEXT = colors.HexColor("#111111")       # Dark Charcoal
COLOR_MUTED = colors.HexColor("#555555")      # Slate


def build_analysis_pdf_report(analysis_record: Dict[str, Any]) -> bytes:
    """
    Generates a high-quality multi-page PDF evaluation report.
    Returns bytes of the compiled PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=COLOR_PRIMARY,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=COLOR_MUTED,
        spaceAfter=10
    )

    heading2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=COLOR_TEXT,
        spaceBefore=12,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=COLOR_TEXT
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=COLOR_TEXT
    )

    meta_key_style = ParagraphStyle(
        "MetaKey",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=COLOR_PRIMARY
    )

    meta_val_style = ParagraphStyle(
        "MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=COLOR_TEXT
    )

    story = []

    # 1. Header Section
    story.append(Paragraph("CAREERMATCH AI — CANDIDATE EVALUATION DOSSIER", title_style))
    story.append(Paragraph("Explainable AI-Based Resume Screening & Multi-Layer Skill Gap Intelligence", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_PRIMARY, spaceBefore=0, spaceAfter=8))

    # 2. Metadata Grid
    job_title = analysis_record.get("job_title", "Software Engineer")
    company = analysis_record.get("company", "Target Employer")
    eval_date = analysis_record.get("created_at", datetime.now().isoformat())[:10]
    model_ver = analysis_record.get("model_version", "2.0.0-xgboost-ontology")
    resume_name = analysis_record.get("resume_filename", "Candidate Resume")
    match_score = float(analysis_record.get("match_score", 0.0))
    fit_cat = analysis_record.get("fit_category", "Moderate Match")

    meta_data = [
        [
            Paragraph("TARGET ROLE:", meta_key_style), Paragraph(str(job_title), meta_val_style),
            Paragraph("EVALUATION DATE:", meta_key_style), Paragraph(str(eval_date), meta_val_style)
        ],
        [
            Paragraph("COMPANY / CONTEXT:", meta_key_style), Paragraph(str(company), meta_val_style),
            Paragraph("MODEL VERSION:", meta_key_style), Paragraph(str(model_ver), meta_val_style)
        ],
        [
            Paragraph("RESUME EVALUATED:", meta_key_style), Paragraph(str(resume_name), meta_val_style),
            Paragraph("REPORT ID:", meta_key_style), Paragraph(f"RPT-{str(analysis_record.get('_id', 'AUTO'))[:8]}", meta_val_style)
        ]
    ]

    meta_table = Table(meta_data, colWidths=[110, 160, 100, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('PADDING', (0,0), (-1,-1), 4),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E4DDEA")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#F0EDF5")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 3. Overall Match Score & Executive Narrative Card
    score_badge_color = COLOR_GREEN if match_score >= 75 else (COLOR_BLUE if match_score >= 50 else COLOR_RED)
    score_html = f"<b><font size=26 color='{score_badge_color.hexval()}'>{match_score:.1f}%</font></b><br/><font size=10 color='{COLOR_TEXT.hexval()}'><b>Fit Rating: {fit_cat}</b></font>"
    
    exec_reasoning = analysis_record.get("executive_reasoning") or analysis_record.get("fit_description", "")
    desc_html = f"<font size=8.5 color='{COLOR_TEXT.hexval()}'><b>Executive Fit Reasoning:</b><br/>{exec_reasoning}</font>"

    score_card_data = [
        [Paragraph(score_html, body_style), Paragraph(desc_html, body_style)]
    ]
    score_card = Table(score_card_data, colWidths=[160, 370])
    score_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_ACCENT),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, COLOR_PRIMARY),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(score_card)
    story.append(Spacer(1, 10))

    # 4. Multi-Dimensional Alignment Table
    story.append(Paragraph("1. Multi-Dimensional Alignment Breakdown", heading2_style))
    dim_scores = analysis_record.get("dimension_scores", {})
    dim_rows = [
        [Paragraph("Alignment Dimension", table_header_style), Paragraph("Score", table_header_style), Paragraph("Evaluation Context", table_header_style)],
        [Paragraph("Overall Semantic Alignment", table_cell_style), Paragraph(f"{dim_scores.get('semantic_alignment', 0):.1f}%", table_cell_style), Paragraph("Dense S-BERT vector cosine similarity of entire resume against JD", table_cell_style)],
        [Paragraph("Skill Ontology Coverage", table_cell_style), Paragraph(f"{dim_scores.get('capability_alignment', 0):.1f}%", table_cell_style), Paragraph("Coverage of explicit skills and ontology-inferred transferable capabilities", table_cell_style)],
        [Paragraph("Experience Compatibility", table_cell_style), Paragraph(f"{dim_scores.get('experience_alignment', 0):.1f}%", table_cell_style), Paragraph("Dedicated tenure compatibility (exceeding experience is never penalized)", table_cell_style)],
        [Paragraph("Education & Tier Alignment", table_cell_style), Paragraph(f"{dim_scores.get('education_alignment', 0):.1f}%", table_cell_style), Paragraph("Degree level, major specialization, and quantitative background", table_cell_style)],
        [Paragraph("Project Relevance Alignment", table_cell_style), Paragraph(f"{dim_scores.get('project_alignment', 0):.1f}%", table_cell_style), Paragraph("Semantic overlap of candidate projects with target responsibilities", table_cell_style)]
    ]
    dim_table = Table(dim_rows, colWidths=[150, 55, 325])
    dim_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('PADDING', (0,0), (-1,-1), 4.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E4DDEA")),
        ('ALIGN', (1,1), (1,-1), 'CENTER'),
    ]))
    story.append(dim_table)
    story.append(Spacer(1, 10))

    # 5. Experience Compatibility Block
    exp_comp = analysis_record.get("nlp_extractions", {}).get("experience_compatibility", {})
    if exp_comp:
        story.append(Paragraph("2. Experience Compatibility Evaluation", heading2_style))
        exp_status = exp_comp.get("status", "MATCH")
        exp_color = COLOR_GREEN if exp_status in ["MATCH", "STRONG MATCH", "EXCEEDS PREFERRED RANGE"] else COLOR_RED
        exp_text = f"<b>Status:</b> <font color='{exp_color.hexval()}'><b>{exp_status}</b></font> (Candidate: {exp_comp.get('candidate_years', 0):.1f} yrs vs Min Required: {exp_comp.get('jd_min_years', 0):.1f} yrs)<br/><b>Finding:</b> {exp_comp.get('reason', '')}"
        exp_table = Table([[Paragraph(exp_text, table_cell_style)]], colWidths=[530])
        exp_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E4DDEA")),
        ]))
        story.append(exp_table)
        story.append(Spacer(1, 10))

    # 6. Evidence-Based Skill Gap & Ontology Matrix
    story.append(Paragraph("3. 3-Tier Skill Gap & Ontology Analysis", heading2_style))
    story.append(Paragraph("Categorizes requirements into Explicit Matches, Related/Inferred Matches, and True Gaps with literal resume evidence.", subtitle_style))
    
    skill_evals = analysis_record.get("nlp_extractions", {}).get("skill_gap_results", {}).get("requirement_evaluations", [])
    gap_rows = [
        [Paragraph("Job Requirement / Skill", table_header_style), Paragraph("Category", table_header_style), Paragraph("Classification Reason & Candidate Evidence", table_header_style)]
    ]
    
    for item in skill_evals[:7]:
        req_text = item.get("requirement", "")
        status = item.get("status", item.get("coverage_status", "Evaluated"))
        reason = item.get("reason", "")
        evidence = item.get("best_evidence", "No direct evidence found.")
        
        status_color = COLOR_GREEN if status == "EXPLICIT MATCH" else (COLOR_BLUE if status == "RELATED MATCH" else COLOR_RED)
        status_p = Paragraph(f"<b><font color='{status_color.hexval()}'>{status}</font></b>", table_cell_style)
        
        reason_and_ev = f"<b>Reason:</b> {reason}<br/><b>Evidence Quote:</b> <i>\"{evidence[:120]}\"</i>"
        
        gap_rows.append([
            Paragraph(req_text[:85] + ("..." if len(req_text) > 85 else ""), table_cell_style),
            status_p,
            Paragraph(reason_and_ev, table_cell_style)
        ])

    gap_table = Table(gap_rows, colWidths=[150, 110, 270])
    gap_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E4DDEA")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(gap_table)
    story.append(Spacer(1, 10))

    # 7. SHAP Explainability Breakdown
    story.append(Paragraph("4. Explainable AI: SHAP Feature Attributions", heading2_style))
    story.append(Paragraph("Exact local Shapley additive values explaining model decision drivers for this specific candidate.", subtitle_style))

    shap_data = analysis_record.get("shap_explanation", {})
    feature_impacts = shap_data.get("feature_impacts", [])

    shap_rows = [
        [Paragraph("Feature Dimension", table_header_style), Paragraph("Value", table_header_style), Paragraph("SHAP Impact", table_header_style), Paragraph("Model Contribution Explanation", table_header_style)]
    ]
    for imp in feature_impacts[:6]:
        feat_name = imp.get("display_name", imp.get("feature_name", ""))
        val = imp.get("feature_value", 0.0)
        shap_pts = imp.get("shap_impact", 0.0)
        expl_text = imp.get("explanation_text", "")
        
        pts_color = COLOR_GREEN if shap_pts > 0 else (COLOR_RED if shap_pts < 0 else COLOR_MUTED)
        sign = "+" if shap_pts > 0 else ""
        pts_p = Paragraph(f"<b><font color='{pts_color.hexval()}'>{sign}{shap_pts:.2f} pts</font></b>", table_cell_style)

        shap_rows.append([
            Paragraph(feat_name, table_cell_style),
            Paragraph(f"{val:.2f}", table_cell_style),
            pts_p,
            Paragraph(expl_text, table_cell_style)
        ])

    shap_table = Table(shap_rows, colWidths=[140, 50, 75, 265])
    shap_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('PADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E4DDEA")),
        ('ALIGN', (1,1), (2,-1), 'CENTER'),
    ]))
    story.append(shap_table)
    story.append(Spacer(1, 10))

    # 8. Actionable Recommendations
    recs = analysis_record.get("recommendations", {})
    story.append(Paragraph("5. Targeted Skill Gap Action Plan", heading2_style))
    summary_advice = recs.get("summary", "Actionable recommendations to accelerate candidacy.")
    story.append(Paragraph(f"<b>Executive Advice:</b> {summary_advice}", body_style))
    story.append(Spacer(1, 6))

    # Projects
    rec_projects = recs.get("recommended_projects", [])
    if rec_projects:
        story.append(Paragraph("<b>Recommended Portfolio Projects:</b>", body_style))
        for p in rec_projects[:2]:
            story.append(Paragraph(f"• <b>{p.get('title', '')}</b>: {p.get('description', '')}", table_cell_style))
        story.append(Spacer(1, 5))

    # Courses
    rec_courses = recs.get("recommended_courses", [])
    if rec_courses:
        story.append(Paragraph("<b>Targeted Bridge Learning:</b>", body_style))
        for c in rec_courses[:2]:
            story.append(Paragraph(f"• <b>{c.get('title', '')}</b> ({c.get('provider', '')}) - Closes: <i>{c.get('closes_gap', '')}</i>", table_cell_style))
        story.append(Spacer(1, 5))

    # 9. Ethical & Responsible AI Footer
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_MUTED, spaceBefore=2, spaceAfter=5))
    disclaimer_text = (
        "<b>Responsible AI Disclosure:</b> CareerMatch AI provides informational resume-to-job alignment insights. "
        "It does not make automated hiring decisions and should not be interpreted as a hiring probability guarantee. "
        "Evaluations are based on dense semantic vector embeddings and an XGBoost model trained on controlled benchmark distributions."
    )
    story.append(Paragraph(disclaimer_text, ParagraphStyle("Disc", parent=body_style, fontSize=6.5, leading=8.5, textColor=COLOR_MUTED)))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
