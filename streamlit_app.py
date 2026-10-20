"""
CareerMatch AI — Interactive Streamlit Showcase & Demonstration Interface.
Provides rapid, interactive live evaluation of the Explainable AI Resume Screening,
Skill Ontology & Transferability Engine, and Experience Compatibility Framework.

Usage:
  streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import io

from ml.predictor import get_predictor
from recommendations.recommendation_engine import generate_recommendations
from reports.pdf_report import build_analysis_pdf_report
from nlp.pdf_reader import extract_text_from_pdf
from nlp.experience_extractor import experience_compatibility, parse_jd_experience_requirements


st.set_page_config(
    page_title="CareerMatch AI — Explainable AI Resume Screening",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #7657B8;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    .score-box {
        background-color: #FAF9FC;
        border: 1px solid #E4DDEA;
        border-radius: 1rem;
        padding: 1.5rem;
        text-align: center;
    }
    .status-explicit {
        color: #137333;
        font-weight: 700;
    }
    .status-related {
        color: #1A73E8;
        font-weight: 700;
    }
    .status-gap {
        color: #C04828;
        font-weight: 700;
    }
    .reason-box {
        background-color: #F8F6FC;
        border-left: 4px solid #7657B8;
        padding: 0.8rem 1rem;
        border-radius: 0.5rem;
        font-size: 0.85rem;
        color: #222222;
        margin-top: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="main-title">CareerMatch AI 🎯</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title"><b>Know Your Job Fit. Before You Apply.</b> — Explainable AI Resume Screening & Multi-Layer Skill Ontology</div>', unsafe_allow_html=True)

# Preset Demos in Sidebar
st.sidebar.header("🧪 Preset Demo Test Cases")
demo_choice = st.sidebar.selectbox(
    "Choose a Benchmark Scenario:",
    [
        "Custom Input (Paste / Upload)",
        "Test 1: Deep Learning vs Keras (Ontology Transfer)",
        "Test 2: Explicit Full Match (Python, Pandas, NumPy)",
        "Test 3: True Gap (React vs Kubernetes)",
        "Test 4: Experience Exceeds (3 yrs vs 0-2 yrs)",
        "Test 5: Freshers Friendly (1 yr vs 0 yrs required)",
        "Test 6: Experience Deficit (1 yr vs 3+ yrs required)"
    ]
)

# Setup Defaults based on selection
default_resume = ""
default_job = ""
default_role = "Machine Learning Engineer"

if demo_choice == "Test 1: Deep Learning vs Keras (Ontology Transfer)":
    default_resume = (
        "Experienced Engineer with deep expertise in Deep Learning, CNN, and Python.\n"
        "Built image classification pipelines and neural architectures. 2 years of experience."
    )
    default_job = (
        "Seeking an AI Engineer with proven skills in:\n"
        "- Machine Learning\n"
        "- Python\n"
        "- Keras\n"
        "Experience: 1-2 years."
    )
    default_role = "AI Engineer"

elif demo_choice == "Test 2: Explicit Full Match (Python, Pandas, NumPy)":
    default_resume = (
        "Data Analyst with 2 years of experience. Proficient in Python, Pandas, NumPy, and Machine Learning.\n"
        "Extensively developed statistical dashboards and predictive tabular models."
    )
    default_job = (
        "Target Role: Data Analyst.\n"
        "Requirements:\n"
        "- Python\n"
        "- Pandas\n"
        "- NumPy\n"
        "Experience: 1+ years."
    )
    default_role = "Data Analyst"

elif demo_choice == "Test 3: True Gap (React vs Kubernetes)":
    default_resume = (
        "Frontend Web Developer with 3 years of experience in React, JavaScript, HTML, and CSS.\n"
        "Built responsive Single Page Applications with Redux and Tailwind."
    )
    default_job = (
        "Cloud Infrastructure Engineer.\n"
        "Key Requirements:\n"
        "- Kubernetes\n"
        "- Container Orchestration\n"
        "- Cloud Infrastructure\n"
        "Experience: 2+ years."
    )
    default_role = "Cloud Engineer"

elif demo_choice == "Test 4: Experience Exceeds (3 yrs vs 0-2 yrs)":
    default_resume = (
        "Software Engineer with 3.0 years of experience in Python, FastAPI, SQL, and Docker.\n"
        "Designed microservice backends with sub-50ms latency."
    )
    default_job = (
        "Junior Backend Developer.\n"
        "Requirements: Python, REST APIs, SQL.\n"
        "Experience: 0-2 years preferred."
    )
    default_role = "Backend Developer"

elif demo_choice == "Test 5: Freshers Friendly (1 yr vs 0 yrs required)":
    default_resume = (
        "Recent graduate with 1.0 year of hands-on project and internship experience in Machine Learning and Python."
    )
    default_job = (
        "Associate Data Scientist. Freshers welcome! No prior experience required.\n"
        "Requirements: Python, Machine Learning fundamentals."
    )
    default_role = "Data Scientist"

elif demo_choice == "Test 6: Experience Deficit (1 yr vs 3+ yrs required)":
    default_resume = (
        "Junior ML Engineer with 1.0 year experience in Python, Scikit-Learn, and SQL."
    )
    default_job = (
        "Senior ML Specialist.\n"
        "Qualifications:\n"
        "- Minimum 3 years of production industry experience.\n"
        "- Python, Machine Learning."
    )
    default_role = "Machine Learning Engineer"

else:
    default_resume = (
        "NAME: Priya Sharma\n"
        "ROLE: Machine Learning Engineer\n"
        "EXPERIENCE: 3.5 years of experience\n"
        "EDUCATION: B.Tech in Artificial Intelligence & Data Science (2022)\n\n"
        "TECHNICAL SKILLS:\n"
        "Python, Scikit-Learn, PyTorch, XGBoost, Docker, FastAPI, AWS EC2, SQL, Deep Learning\n\n"
        "EXPERIENCE:\n"
        "ML Engineer at NovaTech AI Labs (2022 - Present)\n"
        "- Developed and deployed XGBoost tabular fraud detection models on AWS EC2, reducing false positives by 18%.\n"
        "- Containerized ML inference services with Docker and FastAPI, maintaining sub-45ms latency.\n"
        "- Implemented SHAP TreeExplainer to deliver interpretability to fraud investigators."
    )
    default_job = (
        "POSITION: Machine Learning Engineer\n"
        "REQUIRED EXPERIENCE: 2+ years\n"
        "REQUIREMENTS:\n"
        "- Build and deploy machine learning and deep learning pipelines\n"
        "- Demonstrated experience in Python, Scikit-Learn, and PyTorch\n"
        "- Experience deploying containerized APIs with FastAPI and Docker\n"
        "- Knowledge of Keras or TensorFlow is preferred"
    )

# Input Forms
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📄 Candidate Resume")
    uploaded_file = st.file_uploader("Upload Resume PDF (optional)", type=["pdf"])
    if uploaded_file is not None:
        try:
            pdf_bytes = uploaded_file.read()
            extracted_text, _ = extract_text_from_pdf(pdf_bytes, uploaded_file.name)
            resume_input = st.text_area("Resume Content (Extracted)", extracted_text, height=240)
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            resume_input = st.text_area("Resume Content", default_resume, height=240)
    else:
        resume_input = st.text_area("Paste Resume Text", default_resume, height=240)

with col_right:
    st.subheader("📋 Target Job Description")
    target_role_input = st.text_input("Target Role", default_role)
    jd_input = st.text_area("Paste Job Description", default_job, height=240)

# Run Inference Button
if st.button("🚀 Analyze Job Alignment & Skill Ontology", type="primary", use_container_width=True):
    if len(resume_input.strip()) < 15 or len(jd_input.strip()) < 15:
        st.warning("Please provide both a Resume and a Job Description to evaluate.")
    else:
        with st.spinner("Executing S-BERT Embeddings, Skill Ontology Reasoning, XGBoost Regressor, and SHAP TreeExplainer..."):
            predictor = get_predictor()
            result = predictor.predict_match(
                resume_text=resume_input,
                job_description_text=jd_input,
                target_job_role=target_role_input
            )

        match_score = result["match_score"]
        fit_category = result["fit_category"]
        badge_color = result["badge_color"]
        dim_scores = result["dimension_scores"]
        shap_data = result["shap_explanation"]
        nlp_extractions = result["nlp_extractions"]
        skill_gaps = nlp_extractions.get("skill_gap_results", {})
        exp_comp = nlp_extractions.get("experience_compatibility", {})
        evals = skill_gaps.get("requirement_evaluations", [])

        st.divider()

        # 1. Overall Score Display
        top_col1, top_col2 = st.columns([1, 2])
        with top_col1:
            st.markdown(f"""
            <div class="score-box">
                <div style="font-size: 0.8rem; font-weight: 700; color: #7657B8; text-transform: uppercase;">XGBoost Calibrated Score</div>
                <div style="font-size: 3.5rem; font-weight: 900; color: {badge_color};">{match_score:.1f}%</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #111111; margin-top: 0.2rem;">{fit_category}</div>
                <div style="font-size: 0.75rem; color: #777777; margin-top: 0.5rem;">Model: {result['model_version']}</div>
            </div>
            """, unsafe_allow_html=True)

        with top_col2:
            st.markdown("### Executive AI Fit Summary")
            st.markdown(f"*{result['fit_description']}*")
            if result.get("executive_reasoning"):
                st.markdown(f"""
                <div class="reason-box">
                    <b>Reasoning & Domain Synthesis:</b><br/>
                    {result['executive_reasoning']}
                </div>
                """, unsafe_allow_html=True)

        # 2. Multi-Dimensional Radar/Metric Cards
        st.markdown("### 📊 Multi-Dimensional Alignment")
        dim_cols = st.columns(5)
        dim_cols[0].metric("Semantic Fit", f"{dim_scores.get('semantic_alignment', 0)}%")
        dim_cols[1].metric("Skill Ontology", f"{dim_scores.get('capability_alignment', 0)}%")
        dim_cols[2].metric("Experience Fit", f"{dim_scores.get('experience_alignment', 0)}%")
        dim_cols[3].metric("Education Tier", f"{dim_scores.get('education_alignment', 0)}%")
        dim_cols[4].metric("Project Alignment", f"{dim_scores.get('project_alignment', 0)}%")

        st.divider()

        # 3. Experience Compatibility Block
        if exp_comp:
            st.markdown("### ⏳ Fair Experience Compatibility Assessment")
            exp_c1, exp_c2, exp_c3 = st.columns(3)
            exp_c1.metric("Candidate Experience", f"{exp_comp.get('candidate_years', 0):.1f} yrs")
            min_y = exp_comp.get('jd_min_years', 0)
            exp_c2.metric("Stated Requirement", "0 yrs (Freshers welcome)" if min_y == 0 else f"{min_y:.1f}+ yrs")
            status_text = exp_comp.get('status', 'MATCH')
            exp_c3.metric("Compatibility Status", status_text)
            
            st.info(f"**Experience Finding:** {exp_comp.get('reason', '')}")

        st.divider()

        # 4. 3-Tier Skill Gap & Ontology Matrix
        st.markdown("### 🧬 3-Tier Skill Gap & Ontology Matrix")
        st.caption("Classifies every JD requirement into Explicit Match (100%), Related / Inferred Match (Transferable), or True Gap.")

        tab_all, tab_explicit, tab_related, tab_gaps = st.tabs([
            f"All ({len(evals)})",
            f"Explicit Matches ({len(skill_gaps.get('explicit_matches', []))})",
            f"Related / Inferred ({len(skill_gaps.get('related_matches', []))})",
            f"True Gaps ({len(skill_gaps.get('true_gaps', []))})"
        ])

        def render_skill_card(item, idx):
            status = item.get("status", "EXPLICIT MATCH")
            is_explicit = status == "EXPLICIT MATCH" or item.get("is_explicit")
            is_related = status == "RELATED MATCH" or item.get("is_related")
            
            if is_explicit:
                color = "#137333"
                badge = "✓ EXPLICIT MATCH (100% Verified)"
            elif is_related:
                color = "#1A73E8"
                badge = "⚡ RELATED / INFERRED MATCH (Ontology Transferable)"
            else:
                color = "#C04828"
                badge = "✗ TRUE GAP (Unaddressed)"

            st.markdown(f"""
            <div style="border: 1px solid #E4DDEA; border-left: 5px solid {color}; padding: 0.8rem 1rem; border-radius: 0.6rem; margin-bottom: 0.8rem; background-color: #FAF9FC;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; font-size: 0.95rem; color: #111111;">Requirement #{idx}: {item.get('requirement')}</span>
                    <span style="font-weight: 700; font-size: 0.8rem; color: {color};">{badge}</span>
                </div>
                <div style="margin-top: 0.4rem; font-size: 0.85rem; color: #333333;">
                    <b>Relationship Analysis:</b> {item.get('reason', '')}
                </div>
                <div style="margin-top: 0.3rem; font-size: 0.8rem; color: #555555; font-style: italic;">
                    <b>Verified Resume Evidence:</b> "{item.get('best_evidence', '')}"
                </div>
            </div>
            """, unsafe_allow_html=True)

        with tab_all:
            for i, itm in enumerate(evals, 1):
                render_skill_card(itm, i)

        with tab_explicit:
            explicit_list = [i for i in evals if i.get("status") == "EXPLICIT MATCH" or i.get("is_explicit")]
            if explicit_list:
                for i, itm in enumerate(explicit_list, 1):
                    render_skill_card(itm, i)
            else:
                st.write("No explicit skills detected.")

        with tab_related:
            related_list = [i for i in evals if i.get("status") == "RELATED MATCH" or i.get("is_related")]
            if related_list:
                for i, itm in enumerate(related_list, 1):
                    render_skill_card(itm, i)
            else:
                st.write("No related/inferred skills.")

        with tab_gaps:
            gap_list = [i for i in evals if i.get("status") == "TRUE GAP" or (not i.get("is_explicit") and not i.get("is_related"))]
            if gap_list:
                for i, itm in enumerate(gap_list, 1):
                    render_skill_card(itm, i)
            else:
                st.success("No true skill gaps detected!")

        st.divider()

        # 5. SHAP Feature Attributions
        st.markdown("### 🔍 SHAP Local Feature Attributions")
        st.caption("Game-theoretic local feature impacts explaining why this specific score was predicted.")
        
        feature_impacts = shap_data.get("feature_impacts", [])
        if feature_impacts:
            top_feats = feature_impacts[:8]
            chart_df = pd.DataFrame([
                {"Feature": f["display_name"], "SHAP Impact (pts)": f["shap_impact"]}
                for f in top_feats
            ]).set_index("Feature")
            st.bar_chart(chart_df)

        # 6. PDF Report Generation Download
        st.divider()
        st.markdown("### 📥 Download Official Dossier")
        record_for_pdf = {
            "job_title": target_role_input,
            "company": "Target Employer",
            "created_at": "2026-10-20T12:00:00",
            "resume_filename": "Candidate_Resume.pdf",
            "match_score": match_score,
            "fit_category": fit_category,
            "fit_description": result["fit_description"],
            "executive_reasoning": result.get("executive_reasoning"),
            "model_version": result["model_version"],
            "dimension_scores": dim_scores,
            "shap_explanation": shap_data,
            "nlp_extractions": nlp_extractions,
            "recommendations": generate_recommendations(
                skill_gap_results=skill_gaps,
                match_score=match_score,
                dimension_scores=dim_scores
            )
        }
        pdf_bytes = build_analysis_pdf_report(record_for_pdf)
        st.download_button(
            label="Download Complete PDF Evaluation Report",
            data=pdf_bytes,
            file_name="CareerMatch_AI_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
