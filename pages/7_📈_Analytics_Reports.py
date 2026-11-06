"""
TalentRank AI — Recruitment Analytics & Reports Module
Deep statistical insights, talent distribution curves, skill frequency heatmaps,
and enterprise downloadable reports (PDF / CSV).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db import db
from modules.report_generator import report_generator
from utils.helpers import (
    load_custom_css, render_hero_banner, render_kpi_card,
    plot_score_distribution, plot_experience_distribution
)
from utils.export_utils import export_utils

st.set_page_config(page_title="Analytics & Reports — TalentRank AI", page_icon="📈", layout="wide")
load_custom_css()

render_hero_banner(
    title="Recruitment Analytics & Reports",
    subtitle="Aggregate talent pool diagnostics, benchmark analytics, and enterprise exportable compliance reports.",
    badge_text="Executive Analytics"
)

sessions = db.get_all_sessions()
if not sessions:
    st.info("No screening analytics available. Please screen resumes first.")
    st.stop()

# Session Selection
col_s1, col_dl_pdf, col_dl_csv = st.columns([2, 1, 1])
with col_s1:
    sess_dict = {f"Session #{s['session_id']} — {s.get('job_title', '')}": s['session_id'] for s in sessions}
    selected_sess_label = st.selectbox("Select Screening Session for Analytics:", list(sess_dict.keys()))
    active_session_id = sess_dict[selected_sess_label]

results = db.get_session_results(active_session_id)
if not results:
    st.warning("No candidates found in this session.")
    st.stop()

scores = [r.get("final_score", 0.0) for r in results]
avg_score = sum(scores) / len(scores) if scores else 0.0
highest_score = max(scores) if scores else 0.0
lowest_score = min(scores) if scores else 0.0

# Export Buttons
job_name = results[0].get("job_title", "Technical Role")
company_name = results[0].get("company_name", "Enterprise")

with col_dl_pdf:
    pdf_summary = report_generator.generate_candidate_ranking_pdf(
        job_title=job_name,
        company=company_name,
        ranked_candidates=results
    )
    st.download_button(
        "📥 Complete PDF Report",
        data=pdf_summary,
        file_name=f"TalentRank_Analytics_Session_{active_session_id}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with col_dl_csv:
    csv_summary = export_utils.to_csv_bytes(results)
    st.download_button(
        "📊 Export Full CSV",
        data=csv_summary,
        file_name=f"TalentRank_Analytics_Session_{active_session_id}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# Top Statistical KPI Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Total Evaluated", str(len(results)), "Candidates in session", "👥", "kpi-icon-blue")
with c2:
    render_kpi_card("Average Score", f"{avg_score:.1f}%", "Cohort mean", "📈", "kpi-icon-cyan")
with c3:
    render_kpi_card("Highest Match", f"{highest_score:.1f}%", "Top candidate match", "⭐", "kpi-icon-green")
with c4:
    render_kpi_card("Lowest Match", f"{lowest_score:.1f}%", "Baseline score", "📉", "kpi-icon-rose")

st.markdown("<br>", unsafe_allow_html=True)

# Analytics Visualizations
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    fig_dist = plot_score_distribution(scores)
    st.plotly_chart(fig_dist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_g2:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    fig_exp = plot_experience_distribution(results)
    st.plotly_chart(fig_exp, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Most Common Skills in Candidate Pool
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 💡 Skill Frequency in Candidate Pool")

skill_counts = {}
for r in results:
    cand_skills = r.get("matched_skills", []) + r.get("missing_skills", [])
    for s in cand_skills:
        skill_counts[s] = skill_counts.get(s, 0) + 1

if skill_counts:
    df_skills = pd.DataFrame(list(skill_counts.items()), columns=["Skill", "Candidate Count"]).sort_values(by="Candidate Count", ascending=False).head(15)
    fig_skills_freq = px.bar(
        df_skills,
        x="Skill",
        y="Candidate Count",
        color="Candidate Count",
        color_continuous_scale="Viridis",
        title="Top Most Frequent Skills Across Candidate Pool"
    )
    fig_skills_freq.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", size=11),
        margin=dict(t=40, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_skills_freq, use_container_width=True)
