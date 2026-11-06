"""
TalentRank AI — Main Application Entry Point
Production-Ready AI-Powered Resume Intelligence & Candidate Ranking Platform
"""

import streamlit as st
from pathlib import Path
from config import BASE_DIR, DATASET_1_PDF_DIR, DATASET_2_CSV
from database.db import db
from utils.helpers import load_custom_css, render_hero_banner, render_kpi_card

# Page Configuration
st.set_page_config(
    page_title="TalentRank AI — Resume Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Enterprise Custom CSS
load_custom_css()

# Sidebar Branding
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 12px 0 20px 0;">
        <h2 style="margin: 0; color: #38bdf8; font-weight: 800; letter-spacing: -0.02em;">TalentRank <span style="color: #ffffff;">AI</span></h2>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.8rem; letter-spacing: 0.05em;">ENTERPRISE RESUME INTELLIGENCE</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🗂️ Dataset Connectivity")
    
    # Dataset 1 Check
    d1_status = "🟢 Connected (24 Domains)" if DATASET_1_PDF_DIR.exists() else "🔴 Not Found"
    st.markdown(f"**Dataset 1 (Resumes):**<br><span style='font-size:0.85rem; color:#cbd5e1;'>{d1_status}</span>", unsafe_allow_html=True)
    
    # Dataset 2 Check
    d2_status = "🟢 Connected (1.74 GB)" if DATASET_2_CSV.exists() else "🔴 Not Found"
    st.markdown(f"**Dataset 2 (Job Descriptions):**<br><span style='font-size:0.85rem; color:#cbd5e1;'>{d2_status}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("TalentRank AI v2.4 • Production Architecture")

# Main Page Header
render_hero_banner(
    title="TalentRank AI Platform",
    subtitle="Next-generation candidate screening, resume semantic intelligence, and multi-factor ranking. Built with Scikit-learn, TF-IDF Cosine Similarity, PyMuPDF, and Explainable AI.",
    badge_text="Autonomous Recruitment Intelligence"
)

# Quick System Status KPIs
metrics = db.get_dashboard_metrics()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_kpi_card("Candidates Indexed", str(metrics["total_candidates"]), "In persistent database", "👥", "kpi-icon-blue")
with c2:
    render_kpi_card("Screening Runs", str(metrics["total_sessions"]), "Completed screening batches", "📜", "kpi-icon-cyan")
with c3:
    render_kpi_card("Total Scored", str(metrics["total_screened"]), "Evaluated against JDs", "🎯", "kpi-icon-purple")
with c4:
    render_kpi_card("Shortlisted", str(metrics["shortlisted"]), ">= 80% match benchmark", "⭐", "kpi-icon-green")
with c5:
    render_kpi_card("Average Match", f"{metrics['avg_score']}%", "Across all screenings", "📈", "kpi-icon-amber")

st.markdown("<br>", unsafe_allow_html=True)

# Quick Launch Modules Grid
st.markdown("### 🚀 Platform Modules & Navigation")
st.markdown("Select a module from the sidebar or click one of the quick-action cards below:")

col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    st.markdown("""
    <div class="glass-panel" style="min-height: 220px;">
        <div class="panel-header">📄 Resume Screening</div>
        <p style="color: #64748b; font-size: 0.9rem;">
            Upload PDF/DOCX/TXT resumes or load instantly from <b>Dataset 1</b> (24 real industry domains).
            Configure custom scoring weights and initiate multi-factor batch evaluation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Launch Resume Screening →", key="btn_screen", use_container_width=True, type="primary"):
        st.switch_page("pages/2_📄_Resume_Screening.py")

with col_m2:
    st.markdown("""
    <div class="glass-panel" style="min-height: 220px;">
        <div class="panel-header">🏆 Candidate Ranking</div>
        <p style="color: #64748b; font-size: 0.9rem;">
            Explore dynamic leaderboards with multi-criteria tie-breaking. Compare up to 5 candidates side-by-side
            and export audit-ready PDF/CSV reports.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Candidate Ranking →", key="btn_rank", use_container_width=True):
        st.switch_page("pages/3_🏆_Candidate_Ranking.py")

with col_m3:
    st.markdown("""
    <div class="glass-panel" style="min-height: 220px;">
        <div class="panel-header">📋 Job Description Manager</div>
        <p style="color: #64748b; font-size: 0.9rem;">
            Create and edit job descriptions or import real-world roles from <b>Dataset 2</b> (1.74 GB catalog).
            Automatically separates Mandatory vs Preferred skills.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Manage Job Descriptions →", key="btn_jd", use_container_width=True):
        st.switch_page("pages/6_📋_Job_Description_Manager.py")

col_m4, col_m5, col_m6 = st.columns(3)

with col_m4:
    st.markdown("""
    <div class="glass-panel" style="min-height: 220px;">
        <div class="panel-header">🔍 Skill Gap Analysis</div>
        <p style="color: #64748b; font-size: 0.9rem;">
            Inspect candidate vs job requirements across skills, category coverage, and actionable interview questions.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Analyze Skill Gaps →", key="btn_gap", use_container_width=True):
        st.switch_page("pages/5_🔍_Skill_Gap_Analysis.py")

with col_m5:
    st.markdown("""
    <div class="glass-panel" style="min-height: 220px;">
        <div class="panel-header">👤 Candidate Explorer</div>
        <p style="color: #64748b; font-size: 0.9rem;">
            Deep-dive into individual candidate profiles, contact info, multi-dimensional radar scorecards, and recruiter notes.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Explore Profiles →", key="btn_explore", use_container_width=True):
        st.switch_page("pages/4_👤_Candidate_Explorer.py")

with col_m6:
    st.markdown("""
    <div class="glass-panel" style="min-height: 220px;">
        <div class="panel-header">📈 Analytics & Reports</div>
        <p style="color: #64748b; font-size: 0.9rem;">
            Interactive Plotly recruitment analytics, distribution curves, skill demand heatmaps, and downloadable PDF reports.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Analytics →", key="btn_analytics", use_container_width=True):
        st.switch_page("pages/7_📈_Analytics_Reports.py")

st.markdown("<br>", unsafe_allow_html=True)

# Dataset Summary Card
st.markdown("### 📦 Connected Datasets In This Project")
c_d1, c_d2 = st.columns(2)

with c_d1:
    st.info("""
    **Dataset 1 — Kaggle Resume Dataset (Sneha Anbhawal)**
    - **Path:** `Dataset/Dataset 1/`
    - **Components:** `Resume.csv` (56 MB) & `data/data/` (24 category directories of actual PDF resumes).
    - **Use Cases:** Real-time PDF parsing, skill extraction, text preprocessing, and batch screening test runs.
    """)

with c_d2:
    st.success("""
    **Dataset 2 — Kaggle Job Description Dataset (Ravindra Singh Rana)**
    - **Path:** `Dataset/Dataset 2/job_descriptions.csv` (1.74 GB)
    - **Components:** Real-world enterprise postings with roles, required skills, qualifications, and experience.
    - **Use Cases:** Streamed role search, curated job presets, and automatic skill segmentation.
    """)

