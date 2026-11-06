"""
TalentRank AI — Candidate Ranking & Comparative Leaderboard Module
Displays ranked candidate leaderboards with multi-attribute filtering,
side-by-side comparative analysis, and downloadable PDF/CSV reports.
"""

import streamlit as st
import pandas as pd
import plotly.express as go_px
import plotly.graph_objects as go
from database.db import db
from modules.candidate_ranker import candidate_ranker
from modules.report_generator import report_generator
from utils.helpers import load_custom_css, render_hero_banner, get_score_pill_html
from utils.export_utils import export_utils

st.set_page_config(page_title="Candidate Ranking — TalentRank AI", page_icon="🏆", layout="wide")
load_custom_css()

render_hero_banner(
    title="Candidate Ranking Leaderboard",
    subtitle="AI-ranked candidates based on multi-factor skill compatibility, TF-IDF semantic overlap, and experience alignment.",
    badge_text="Algorithmic Decision Support"
)

# Fetch screening sessions
sessions = db.get_all_sessions()
if not sessions:
    st.info("No screening sessions found in the database. Please navigate to Resume Screening to screen candidates.")
    if st.button("Go to Resume Screening →"):
        st.switch_page("pages/2_📄_Resume_Screening.py")
    st.stop()

# Session Selector
session_dict = {f"Session #{s['session_id']} — {s.get('job_title', 'Untitled')} ({s.get('screening_date', '')[:16]})": s['session_id'] for s in sessions}

col_sess, col_dl_pdf, col_dl_csv = st.columns([2, 1, 1])
with col_sess:
    selected_sess_label = st.selectbox("Select Screening Session:", list(session_dict.keys()))
    active_session_id = session_dict[selected_sess_label]

results = db.get_session_results(active_session_id)
ranked_candidates = candidate_ranker.rank_candidates(results)

# PDF & CSV Export buttons
if ranked_candidates:
    current_job_title = ranked_candidates[0].get("job_title", "Software Engineer")
    current_company = ranked_candidates[0].get("company_name", "Enterprise")

    with col_dl_pdf:
        pdf_bytes = report_generator.generate_candidate_ranking_pdf(
            job_title=current_job_title,
            company=current_company,
            ranked_candidates=ranked_candidates
        )
        st.download_button(
            "📥 Download PDF Report",
            data=pdf_bytes,
            file_name=f"TalentRank_Ranking_Session_{active_session_id}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with col_dl_csv:
        csv_bytes = export_utils.to_csv_bytes(ranked_candidates)
        st.download_button(
            "📊 Export to CSV",
            data=csv_bytes,
            file_name=f"TalentRank_Ranking_Session_{active_session_id}.csv",
            mime="text/csv",
            use_container_width=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# Search & Filters Card
with st.expander("🔍 Search & Filter Leaderboard", expanded=True):
    f_c1, f_c2, f_c3, f_c4 = st.columns(4)
    with f_c1:
        search_query = st.text_input("Search Candidate Name / Resume", placeholder="e.g. Rahul, John...")
    with f_c2:
        score_range = st.slider("Score Range (%)", 0, 100, (0, 100))
    with f_c3:
        rec_filter = st.selectbox("Screening Recommendation", ["All", "Strong Match", "Good Match", "Partial Match", "Needs Review"])
    with f_c4:
        display_limit = st.radio("Display Scope", ["Top 5", "Top 10", "All Candidates"], horizontal=True)

# Filter application
filtered = candidate_ranker.filter_candidates(
    ranked_candidates,
    min_score=float(score_range[0]),
    max_score=float(score_range[1]),
    recommendation=rec_filter,
    search_query=search_query
)

if display_limit == "Top 5":
    filtered = filtered[:5]
elif display_limit == "Top 10":
    filtered = filtered[:10]

st.markdown(f"**Displaying {len(filtered)} candidate(s)** out of {len(ranked_candidates)} total evaluated.")

# Main Interactive Ranking Table
if filtered:
    table_data = []
    for c in filtered:
        rec = c.get("recommendation", "Review")
        table_data.append({
            "Rank": f"#{c.get('rank', '-')}",
            "Candidate Name": c.get("candidate_name", "Unknown"),
            "Final Score": f"{c.get('final_score', 0):.1f}%",
            "Recommendation": rec,
            "Req Skills Matched": f"{len(c.get('matched_required', []))} matched",
            "Missing Req Skills": ", ".join(c.get("missing_required", [])) or "None",
            "TF-IDF Similarity": f"{c.get('similarity_score', 0):.1f}%",
            "Experience": f"{c.get('candidate_exp', 0.0):.1f} yrs",
            "Email": c.get("email", "Not Found")
        })

    df_display = pd.DataFrame(table_data)
    st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.warning("No candidates matched the specified filter criteria.")

st.markdown("<br>", unsafe_allow_html=True)

# Candidate Side-by-Side Comparison Tool
st.markdown("### ⚖️ Side-by-Side Candidate Comparison")
st.markdown("Select up to **5 candidates** to benchmark qualification metrics, skill overlaps, and scoring vectors simultaneously:")

candidate_map = {f"#{c.get('rank')} {c.get('candidate_name')} ({c.get('final_score'):.1f}%)": c for c in ranked_candidates}
selected_for_comp = st.multiselect(
    "Choose candidates to compare:",
    options=list(candidate_map.keys()),
    default=list(candidate_map.keys())[:min(3, len(candidate_map))],
    max_selections=5
)

if selected_for_comp:
    comp_list = [candidate_map[k] for k in selected_for_comp]
    df_comp = candidate_ranker.build_comparison_dataframe(comp_list)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    # Multi-Candidate Radar / Bar Visualization
    c_radar, c_bar = st.columns(2)

    with c_radar:
        st.markdown("<h4 style='font-size:1rem; font-weight:700;'>Comparative Radar Profile</h4>", unsafe_allow_html=True)
        fig_radar = go.Figure()
        categories = ["Req Skills", "Similarity", "Pref Skills", "Experience", "Education", "Keywords"]

        colors = ["#0284c7", "#10b981", "#f59e0b", "#9333ea", "#ef4444"]
        for idx, c in enumerate(comp_list):
            vals = [
                c.get("skill_score", 0),
                c.get("similarity_score", 0),
                c.get("preferred_skill_score", 0),
                c.get("experience_score", 0),
                c.get("education_score", 0),
                c.get("keyword_score", 0)
            ]
            vals.append(vals[0])
            cats_closed = categories + [categories[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals,
                theta=cats_closed,
                fill='toself',
                name=c.get("candidate_name")[:15],
                line=dict(color=colors[idx % len(colors)])
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=30, b=30, l=30, r=30),
            font=dict(family="Plus Jakarta Sans", size=11)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with c_bar:
        st.markdown("<h4 style='font-size:1rem; font-weight:700;'>Overall Score Comparison</h4>", unsafe_allow_html=True)
        names = [c.get("candidate_name", "Unknown") for c in comp_list]
        final_scores = [c.get("final_score", 0.0) for c in comp_list]
        fig_bar = go.Figure(go.Bar(
            x=names,
            y=final_scores,
            marker_color="#0284c7",
            text=[f"{s:.1f}%" for s in final_scores],
            textposition="auto"
        ))
        fig_bar.update_layout(
            yaxis=dict(range=[0, 105], title="Score (%)"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=30, b=20, l=20, r=20),
            font=dict(family="Plus Jakarta Sans", size=11)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
