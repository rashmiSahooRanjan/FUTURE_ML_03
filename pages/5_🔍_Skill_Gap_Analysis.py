"""
TalentRank AI — Skill Gap Analysis Module
Analyzes candidate-job requirement divergence, category-wise skill coverage,
and generates targeted technical interview prompts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import db
from modules.skill_gap_analyzer import skill_gap_analyzer
from utils.helpers import load_custom_css, render_hero_banner, render_kpi_card, render_skill_badges

st.set_page_config(page_title="Skill Gap Analysis — TalentRank AI", page_icon="🔍", layout="wide")
load_custom_css()

render_hero_banner(
    title="Skill Gap & Competency Matrix",
    subtitle="Pinpoint missing technical prerequisites, analyze domain coverage, and streamline technical interviewing.",
    badge_text="Competency Diagnostic"
)

# Fetch sessions
sessions = db.get_all_sessions()
if not sessions:
    st.info("No candidates available for skill gap analysis. Please screen resumes first.")
    st.stop()

col_s, col_c = st.columns([1, 1.5])
with col_s:
    sess_dict = {f"Session #{s['session_id']} — {s.get('job_title', '')}": s['session_id'] for s in sessions}
    selected_sess_id = st.selectbox("Select Screening Session:", list(sess_dict.keys()))
    active_session_id = sess_dict[selected_sess_id]

results = db.get_session_results(active_session_id)
if not results:
    st.warning("No candidates found in this session.")
    st.stop()

with col_c:
    cand_options = {f"#{c.get('final_score'):.1f}% — {c.get('candidate_name', 'Unknown')}": c for c in results}
    selected_cand_label = st.selectbox("Select Candidate to Evaluate:", list(cand_options.keys()))
    candidate = cand_options[selected_cand_label]

job = db.get_job_description(results[0].get("job_id", 1))
required_skills = job.get("required_skills", []) if job else []
preferred_skills = job.get("preferred_skills", []) if job else []

cand_record = db.get_candidate(candidate["candidate_id"])
candidate_skills = cand_record.get("extracted_skills", []) if cand_record else []

# Perform Skill Gap Analysis
analysis = skill_gap_analyzer.analyze_skill_gap(candidate_skills, required_skills, preferred_skills)

st.markdown("<br>", unsafe_allow_html=True)

# Top KPI Summary Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Mandatory Coverage", f"{analysis['mandatory_coverage_pct']}%", f"{analysis['matched_mandatory']} of {analysis['total_mandatory']} skills", "🎯", "kpi-icon-blue")
with c2:
    render_kpi_card("Missing Mandatory", str(analysis['missing_mandatory']), "Critical requirements", "⚠️", "kpi-icon-rose")
with c3:
    render_kpi_card("Preferred Coverage", f"{analysis['preferred_coverage_pct']}%", f"{analysis['matched_preferred']} of {analysis['total_preferred']} skills", "✨", "kpi-icon-green")
with c4:
    render_kpi_card("Additional Skills", str(len(analysis['additional_skills'])), "Bonus profile skills", "💡", "kpi-icon-purple")

st.markdown("<br>", unsafe_allow_html=True)

# Visualizations and Breakdown
col_table, col_chart = st.columns([1.3, 1])

with col_table:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>📋 Requirement vs Candidate Skill Matrix</div>", unsafe_allow_html=True)
    if not analysis["matrix_df"].empty:
        # Style status column
        styled_df = analysis["matrix_df"].copy()
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("No explicit skills extracted from the active job description.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_chart:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>📊 Category Coverage (%)</div>", unsafe_allow_html=True)
    if not analysis["coverage_df"].empty:
        fig_cov = px.bar(
            analysis["coverage_df"],
            x="Coverage (%)",
            y="Category",
            orientation="h",
            color="Coverage (%)",
            color_continuous_scale=[[0, '#ef4444'], [0.5, '#f59e0b'], [1.0, '#10b981']],
            range_x=[0, 105],
            text="Coverage (%)"
        )
        fig_cov.update_layout(
            margin=dict(t=20, b=20, l=100, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            font=dict(family="Plus Jakarta Sans", size=11)
        )
        st.plotly_chart(fig_cov, use_container_width=True)
    else:
        st.info("No category data available.")
    st.markdown('</div>', unsafe_allow_html=True)

# Actionable Interview Prompts
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🎯 Recommended Technical Interview Questions")

missing_mandatory = [row["Skill"] for _, row in analysis["matrix_df"].iterrows() if row["Type"] == "Mandatory" and row["Status"] == "Missing"]

if missing_mandatory:
    st.markdown(f"Because the candidate's resume does not explicitly document **{', '.join(missing_mandatory[:4])}**, focus interview questions on:")
    for skill in missing_mandatory[:5]:
        st.markdown(f"""
        - **{skill}:** *"Can you describe a practical production scenario where you utilized {skill}? How did you handle edge cases and architectural constraints?"*
        """)
else:
    st.success("🎉 The candidate matches all mandatory technical skills listed for this role! Focus interview questions on architecture, systems design, and cultural alignment.")

