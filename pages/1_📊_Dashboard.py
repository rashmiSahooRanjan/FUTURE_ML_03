"""
TalentRank AI — Main Recruitment Analytics Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db import db
from utils.helpers import (
    load_custom_css, render_hero_banner, render_kpi_card,
    plot_score_distribution, plot_top_candidates, plot_skill_demand,
    plot_experience_distribution
)
from utils.dataset_loader import dataset_loader

st.set_page_config(page_title="Recruitment Dashboard — TalentRank AI", page_icon="📊", layout="wide")
load_custom_css()

render_hero_banner(
    title="Recruitment Analytics Dashboard",
    subtitle="Real-time candidate intelligence, score distributions, and talent pipeline diagnostics.",
    badge_text="Executive Recruitment Overview"
)

# Fetch current metrics from DB
metrics = db.get_dashboard_metrics()
all_sessions = db.get_all_sessions()
all_candidates = db.get_all_candidates()

# Quick Demo Run if DB is empty
if metrics["total_screened"] == 0:
    st.info("💡 **Welcome to TalentRank AI!** No candidate screening data is recorded yet. You can launch a quick 1-click batch screening using the connected datasets below to populate this dashboard immediately.")
    col_demo, _ = st.columns([1, 2])
    with col_demo:
        if st.button("🚀 Load Demo Batch from Dataset 1 & 2", type="primary", use_container_width=True):
            with st.spinner("Processing real resumes from Dataset 1 against tech role from Dataset 2..."):
                # 1. Load job
                curated = dataset_loader.load_curated_jobs()
                job_spec = curated[0] if curated else {
                    "job_title": "Python & Data Science Developer",
                    "company": "Tech Corp",
                    "description": "Looking for Python, SQL, Machine Learning, Pandas, and Git developer with 2+ years exp.",
                    "experience": "2 Years",
                    "qualifications": "Bachelor Degree"
                }
                from modules.job_parser import job_parser
                parsed_job = job_parser.parse_job(job_spec["job_title"], job_spec.get("description", ""), job_spec.get("company", "Tech Corp"))
                job_id = db.save_job_description(parsed_job)
                parsed_job["job_id"] = job_id

                # 2. Load 8 real PDFs from Dataset 1
                resumes = dataset_loader.load_resumes_from_pdfs("INFORMATION-TECHNOLOGY", limit=8)
                if not resumes:
                    # fallback to CSV if PDF directory empty
                    resumes = dataset_loader.load_resumes_from_csv("INFORMATION-TECHNOLOGY", limit=8)

                # 3. Score and save
                from modules.scoring_engine import scoring_engine
                from modules.candidate_ranker import candidate_ranker

                session_id = db.create_screening_session(job_id, len(resumes), len(resumes))
                scored = []
                for r in resumes:
                    cid = db.save_candidate(r)
                    r["candidate_id"] = cid
                    res = scoring_engine.score_candidate(r, parsed_job)
                    res["session_id"] = session_id
                    db.save_screening_result(res)
                    scored.append(res)
            st.success("Demo batch successfully screened and saved to database!")
            st.rerun()

# KPI Metric Cards Grid
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    render_kpi_card("Total Resumes", str(metrics["total_candidates"]), "In database index", "📄", "kpi-icon-blue")
with c2:
    render_kpi_card("Evaluated", str(metrics["total_screened"]), "Completed evaluations", "🎯", "kpi-icon-cyan")
with c3:
    render_kpi_card("Shortlisted", str(metrics["shortlisted"]), "Score >= 80%", "⭐", "kpi-icon-green")
with c4:
    render_kpi_card("Under Review", str(metrics["needs_review"]), "Score < 45%", "⚠️", "kpi-icon-rose")
with c5:
    render_kpi_card("Avg Match Score", f"{metrics['avg_score']}%", "Overall candidates", "📈", "kpi-icon-amber")
with c6:
    total_skills = sum(len(c.get("extracted_skills", [])) for c in all_candidates)
    render_kpi_card("Skills Indexed", str(total_skills), "Extracted from pool", "💡", "kpi-icon-purple")

st.markdown("<br>", unsafe_allow_html=True)

# Visualizations Row 1
col_v1, col_v2 = st.columns(2)

# Get latest session results for visualization
latest_results = []
if all_sessions:
    latest_session_id = all_sessions[0]["session_id"]
    latest_results = db.get_session_results(latest_session_id)

scores = [r.get("final_score", 0.0) for r in latest_results]

with col_v1:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    if scores:
        fig_dist = plot_score_distribution(scores)
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.info("No score distributions available. Please screen resumes.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_v2:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    if latest_results:
        fig_top = plot_top_candidates(latest_results, top_n=8)
        st.plotly_chart(fig_top, use_container_width=True)
    else:
        st.info("No candidate rankings to display.")
    st.markdown('</div>', unsafe_allow_html=True)

# Visualizations Row 2
col_v3, col_v4, col_v5 = st.columns([1.2, 1.2, 1])

with col_v3:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    # Skill demand from active job
    if all_sessions:
        job = db.get_job_description(all_sessions[0]["job_id"])
        req_skills = job.get("required_skills", []) if job else ["Python", "SQL", "Git"]
        fig_skills = plot_skill_demand(req_skills[:10])
        st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.info("No job skill demand data.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_v4:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    if latest_results:
        fig_exp = plot_experience_distribution(latest_results)
        st.plotly_chart(fig_exp, use_container_width=True)
    else:
        st.info("No experience data available.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_v5:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<h4 style='font-size:1rem; font-weight:700;'>Resume Processing Overview</h4>", unsafe_allow_html=True)
    proc_df = pd.DataFrame({
        "Status": ["Successfully Processed", "Scanned / Failed"],
        "Count": [len(latest_results), 0 if latest_results else 1]
    })
    fig_proc = px.pie(
        proc_df,
        values="Count",
        names="Status",
        hole=0.6,
        color_discrete_sequence=["#10b981", "#ef4444"]
    )
    fig_proc.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_proc, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Recent Screening Activity Table
st.markdown("### 📋 Recent Screening Activity")
if latest_results:
    table_rows = []
    for r in latest_results[:10]:
        table_rows.append({
            "Candidate Name": r.get("candidate_name", "Unknown"),
            "Job Role": r.get("job_title", "General Role"),
            "Match Score": f"{r.get('final_score', 0):.1f}%",
            "Screening Status": r.get("screening_status") or r.get("recommendation", "Under Review"),
            "Date": r.get("screening_date", "Recent")[:16] if r.get("screening_date") else "Today"
        })
    df_recent = pd.DataFrame(table_rows)
    st.dataframe(df_recent, use_container_width=True, hide_index=True)
else:
    st.info("No recent screening activities found.")

