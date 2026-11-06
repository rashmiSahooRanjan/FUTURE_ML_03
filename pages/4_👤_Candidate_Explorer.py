"""
TalentRank AI — Candidate Explorer Module
Deep-dive individual candidate profiles with multi-attribute scorecard,
explainable AI narratives, recruiter notes management, and PDF dossier download.
"""

import streamlit as st
import pandas as pd
from database.db import db
from modules.explainability import explainability_engine
from modules.report_generator import report_generator
from utils.helpers import (
    load_custom_css, render_hero_banner, render_kpi_card,
    render_skill_badges, plot_candidate_radar
)

st.set_page_config(page_title="Candidate Explorer — TalentRank AI", page_icon="👤", layout="wide")
load_custom_css()

render_hero_banner(
    title="Candidate Explorer & Dossier",
    subtitle="Detailed talent profile diagnostics, explainable scoring vectors, and recruiter screening notes.",
    badge_text="Candidate Profile Intelligence"
)

# Fetch sessions
sessions = db.get_all_sessions()
if not sessions:
    st.info("No candidates available. Please run a resume screening first.")
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
    cand_options = {f"#{c.get('final_score'):.1f}% — {c.get('candidate_name', 'Unknown')} ({c.get('resume_filename', '')[:25]})": c for c in results}
    selected_cand_label = st.selectbox("Select Candidate to Inspect:", list(cand_options.keys()))
    candidate = cand_options[selected_cand_label]

st.markdown("<br>", unsafe_allow_html=True)

# Fetch Job Specs for Context & Explanation
job_info = db.get_job_description(results[0].get("job_id", 1)) or {
    "job_title": candidate.get("job_title", "Technical Role"),
    "minimum_experience": candidate.get("required_exp", 0.0),
    "education_requirement": "Bachelor's Degree",
    "required_skills": [],
    "preferred_skills": []
}

# Generate Explainable AI Analysis
explanation = explainability_engine.generate_explanation(candidate, job_info)

# Profile Header & Top Metrics
col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
with col_p1:
    render_kpi_card("Overall Match", f"{candidate.get('final_score', 0):.1f}%", candidate.get("recommendation", "Review"), "🎯", "kpi-icon-blue")
with col_p2:
    render_kpi_card("Req. Skills", f"{candidate.get('skill_score', 0):.1f}%", f"{len(candidate.get('matched_skills', []))} matched", "💡", "kpi-icon-cyan")
with col_p3:
    render_kpi_card("Similarity", f"{candidate.get('similarity_score', 0):.1f}%", "TF-IDF Cosine", "🧠", "kpi-icon-purple")
with col_p4:
    render_kpi_card("Experience", f"{candidate.get('candidate_exp', 0):.1f} yrs", f"Req: {job_info.get('minimum_experience', 0):.1f} yrs", "⏳", "kpi-icon-amber")
with col_p5:
    render_kpi_card("Education", f"{candidate.get('education_score', 0):.1f}%", candidate.get("candidate_edu", "Degree")[:12], "🎓", "kpi-icon-green")

st.markdown("<br>", unsafe_allow_html=True)

# Layout: Left column Contact & Radar, Right column Details & Explanations
col_left, col_right = st.columns([1, 1.4])

with col_left:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>👤 Contact & Personal Information</div>", unsafe_allow_html=True)
    st.markdown(f"**Name:** {candidate.get('candidate_name', 'Unknown')}")
    st.markdown(f"**Email:** `{candidate.get('email', 'Not Found')}`")
    st.markdown(f"**Phone:** `{candidate.get('phone', 'Not Found')}`")
    st.markdown(f"**Location:** {candidate.get('location', 'Not Specified')}")
    st.markdown(f"**Education Details:** {candidate.get('candidate_edu', 'Not Specified')}")
    st.markdown(f"**Resume Source:** `{candidate.get('resume_filename', '')}`")

    # Links
    links = []
    if candidate.get("linkedin") and candidate.get("linkedin") != "Not Found":
        links.append(f"[LinkedIn Profile]({candidate['linkedin']})")
    if candidate.get("github") and candidate.get("github") != "Not Found":
        links.append(f"[GitHub Profile]({candidate['github']})")
    if candidate.get("portfolio") and candidate.get("portfolio") != "Not Found":
        links.append(f"[Portfolio Link]({candidate['portfolio']})")

    if links:
        st.markdown("**Web Presence:** " + " • ".join(links))

    st.markdown('</div>', unsafe_allow_html=True)

    # Radar chart
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>📊 Multi-Dimensional Alignment</div>", unsafe_allow_html=True)
    fig_radar = plot_candidate_radar(candidate)
    st.plotly_chart(fig_radar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    # Explainable AI Insights Box
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>🧠 Explainable AI Decision Support</div>", unsafe_allow_html=True)
    st.markdown(f"**Algorithmic Synthesis:**<br>{explanation['summary_narrative']}", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c_str, c_gap = st.columns(2)
    with c_str:
        st.markdown("<b style='color:#16a34a;'>✅ Demonstrated Strengths:</b>", unsafe_allow_html=True)
        for s in explanation["strengths"]:
            st.markdown(f"• {s}")
    with c_gap:
        st.markdown("<b style='color:#dc2626;'>⚠️ Areas to Verify / Gaps:</b>", unsafe_allow_html=True)
        for g in explanation["gaps"]:
            st.markdown(f"• {g}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Skill Badges
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>💡 Skill Inventory Breakdown</div>", unsafe_allow_html=True)
    
    st.markdown("**Matched Skills (Required & Preferred):**")
    st.markdown(render_skill_badges(candidate.get("matched_skills", []), "matched"), unsafe_allow_html=True)
    
    st.markdown("<br>**Missing Required Skills:**", unsafe_allow_html=True)
    st.markdown(render_skill_badges(candidate.get("missing_skills", []), "missing"), unsafe_allow_html=True)
    
    cand_record = db.get_candidate(candidate["candidate_id"])
    all_cand_skills = cand_record.get("extracted_skills", []) if cand_record else []
    additional = [s for s in all_cand_skills if s not in candidate.get("matched_skills", [])]
    if additional:
        st.markdown("<br>**Additional Skills Found on Resume:**", unsafe_allow_html=True)
        st.markdown(render_skill_badges(additional, "additional"), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Recruiter Notes & Pipeline Status Management
st.markdown("### 📝 Recruiter Notes & Status Management")
with st.container():
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    c_status, c_btn = st.columns([2, 1])

    with c_status:
        current_status = candidate.get("screening_status") or "Under Review"
        status_options = ["Under Review", "Shortlisted", "Interview Scheduled", "Offer Extended", "Rejected"]
        idx = status_options.index(current_status) if current_status in status_options else 0
        new_status = st.selectbox("Candidate Hiring Status:", status_options, index=idx)

    notes_text = st.text_area(
        "Recruiter Internal Evaluation Notes:",
        value=candidate.get("notes") or "",
        placeholder="Add interview observations, compensation alignment, or verification points..."
    )

    if st.button("💾 Save Notes & Status", type="primary"):
        db.update_candidate_notes(
            candidate_id=candidate["candidate_id"],
            session_id=active_session_id,
            notes=notes_text,
            status=new_status
        )
        st.success("Candidate notes and pipeline status successfully updated!")
    st.markdown('</div>', unsafe_allow_html=True)

# Download Individual PDF Dossier
st.markdown("<br>", unsafe_allow_html=True)
col_pdf_dl, _ = st.columns([1, 2])
with col_pdf_dl:
    pdf_cand_bytes = report_generator.generate_candidate_report_pdf(
        candidate_data=candidate,
        job_data=job_info,
        explanation=explanation
    )
    st.download_button(
        label="📥 Download Full Candidate Dossier (PDF)",
        data=pdf_cand_bytes,
        file_name=f"TalentRank_Candidate_{candidate.get('candidate_id')}_{candidate.get('candidate_name', 'Report').replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
