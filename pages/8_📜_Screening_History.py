"""
TalentRank AI — Screening History Module
Archive and audit previous screening runs, compare cohort performances,
and manage persistent historical records in SQLite.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database.db import db
from utils.helpers import load_custom_css, render_hero_banner, render_kpi_card

st.set_page_config(page_title="Screening History — TalentRank AI", page_icon="📜", layout="wide")
load_custom_css()

render_hero_banner(
    title="Screening History & Session Audit",
    subtitle="Access historical screening runs, track cohort evolution, and audit past hiring decisions.",
    badge_text="Audit & Compliance Log"
)

all_sessions = db.get_all_sessions()
if not all_sessions:
    st.info("No past screening sessions recorded.")
    st.stop()

# Search Sessions
search_term = st.text_input("🔍 Search Historical Sessions by Role or Company:", placeholder="e.g. Developer, Tech Corp...")

filtered_sessions = all_sessions
if search_term:
    q = search_term.lower()
    filtered_sessions = [
        s for s in all_sessions
        if q in str(s.get("job_title", "")).lower() or q in str(s.get("company_name", "")).lower()
    ]

# Summary Table
table_data = []
for s in filtered_sessions:
    table_data.append({
        "Session ID": f"#{s['session_id']}",
        "Job Title": s.get("job_title", "Untitled"),
        "Company": s.get("company_name", "Confidential"),
        "Screening Date": str(s.get("screening_date", ""))[:16],
        "Resumes Processed": s.get("processed_resumes", 0),
        "Avg Match Score": f"{s.get('avg_score', 0):.1f}%" if s.get('avg_score') else "N/A",
        "Top Score": f"{s.get('max_score', 0):.1f}%" if s.get('max_score') else "N/A"
    })

st.markdown("### 🗃️ Historical Screening Sessions")
df_sessions = pd.DataFrame(table_data)
st.dataframe(df_sessions, use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# Deep Inspect / Delete Session
st.markdown("### 🔍 Inspect or Manage Session")
sess_options = {f"Session #{s['session_id']} — {s.get('job_title', '')} ({s.get('screening_date', '')[:10]})": s['session_id'] for s in filtered_sessions}
selected_key = st.selectbox("Select Session to Manage:", list(sess_options.keys()))
chosen_session_id = sess_options[selected_key]

c_action1, c_action2, _ = st.columns([1.2, 1.2, 2])

with c_action1:
    if st.button("📊 Open in Candidate Ranking", type="primary", use_container_width=True):
        st.session_state["active_session_id"] = chosen_session_id
        st.switch_page("pages/3_🏆_Candidate_Ranking.py")

with c_action2:
    if st.button("🗑️ Delete Screening Session", type="secondary", use_container_width=True):
        db.delete_screening_session(chosen_session_id)
        st.success(f"Session #{chosen_session_id} successfully deleted!")
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Compare Two Historical Sessions
st.markdown("### ⚖️ Compare Two Screening Sessions")
if len(all_sessions) >= 2:
    c_cmp1, c_cmp2 = st.columns(2)
    with c_cmp1:
        s1_choice = st.selectbox("Cohort A:", list(sess_dict.keys()) if 'sess_dict' in locals() else list(sess_options.keys()), index=0, key="cmp_s1")
        s1_id = sess_options[s1_choice]
    with c_cmp2:
        s2_choice = st.selectbox("Cohort B:", list(sess_dict.keys()) if 'sess_dict' in locals() else list(sess_options.keys()), index=min(1, len(sess_options)-1), key="cmp_s2")
        s2_id = sess_options[s2_choice]

    res1 = db.get_session_results(s1_id)
    res2 = db.get_session_results(s2_id)

    avg1 = sum(r.get("final_score", 0) for r in res1) / len(res1) if res1 else 0
    avg2 = sum(r.get("final_score", 0) for r in res2) / len(res2) if res2 else 0

    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Bar(
        x=["Cohort A", "Cohort B"],
        y=[avg1, avg2],
        marker_color=["#0284c7", "#10b981"],
        text=[f"{avg1:.1f}%", f"{avg2:.1f}%"],
        textposition="auto"
    ))
    fig_cmp.update_layout(
        title="Average Cohort Match Score Comparison",
        yaxis=dict(range=[0, 105], title="Score (%)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=20, l=20, r=20),
        font=dict(family="Plus Jakarta Sans", size=12)
    )
    st.plotly_chart(fig_cmp, use_container_width=True)
else:
    st.info("Run at least two screening sessions to enable cohort comparison.")

