"""
TalentRank AI — Job Description Manager Module
Manage, create, edit, and delete job postings.
Deeply integrated with Dataset 2 (1.74 GB catalog) with real-time search and curated templates.
"""

import streamlit as st
import json
from database.db import db
from modules.job_parser import job_parser
from utils.helpers import load_custom_css, render_hero_banner, render_skill_badges
from utils.dataset_loader import dataset_loader

st.set_page_config(page_title="Job Manager — TalentRank AI", page_icon="📋", layout="wide")
load_custom_css()

render_hero_banner(
    title="Job Description Manager",
    subtitle="Create, configure, and maintain target job profiles. Search and import thousands of real-world role requirements from Dataset 2.",
    badge_text="Requisition Intelligence"
)

tab_create, tab_dataset2, tab_manage = st.tabs([
    "➕ Create New Requisition",
    "📦 Import from Dataset 2 (Job Catalog)",
    "🗂️ Manage Saved Requisitions"
])

# --- TAB 1: Create New Job Description ---
with tab_create:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>Job Details & Specifications</div>", unsafe_allow_html=True)

    c_t1, c_t2 = st.columns([1.5, 1])
    with c_t1:
        job_title = st.text_input("Job Title*", placeholder="e.g. Lead Machine Learning Engineer")
    with c_t2:
        company_name = st.text_input("Company Name*", placeholder="e.g. Antigravity Cloud Labs")

    job_desc_text = st.text_area(
        "Job Description & Role Responsibilities*",
        placeholder="Paste full job description including requirements, qualifications, and tech stack...",
        height=160
    )

    c_e1, c_e2 = st.columns(2)
    with c_e1:
        min_exp = st.number_input("Minimum Experience (Years)", min_value=0.0, max_value=30.0, value=3.0, step=0.5)
    with c_e2:
        edu_req = st.selectbox(
            "Education Requirement",
            ["Bachelor's Degree", "Master's Degree", "Ph.D. / Doctorate", "Diploma / Associate", "Any Degree"]
        )

    # Auto-extract preview button
    if st.button("🔍 Auto-Extract Skills & Requirements"):
        if job_desc_text:
            parsed = job_parser.parse_job(job_title, job_desc_text, company_name)
            st.session_state["extracted_req_skills"] = parsed["required_skills"]
            st.session_state["extracted_pref_skills"] = parsed["preferred_skills"]
            st.success("Extracted skills successfully! Review and modify below.")
        else:
            st.warning("Please provide a job description first.")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        req_skills_input = st.text_input(
            "Mandatory / Required Skills (comma-separated)",
            value=", ".join(st.session_state.get("extracted_req_skills", ["Python", "Machine Learning", "SQL", "Git"]))
        )
    with col_s2:
        pref_skills_input = st.text_input(
            "Preferred / Nice-to-Have Skills (comma-separated)",
            value=", ".join(st.session_state.get("extracted_pref_skills", ["Docker", "AWS", "FastAPI"]))
        )

    if st.button("💾 Save Requisition to Database", type="primary"):
        if not job_title or not job_desc_text:
            st.error("Please fill in the Job Title and Job Description.")
        else:
            req_list = [s.strip() for s in req_skills_input.split(",") if s.strip()]
            pref_list = [s.strip() for s in pref_skills_input.split(",") if s.strip()]
            job_record = {
                "job_title": job_title,
                "company_name": company_name or "Confidential",
                "description": job_desc_text,
                "required_skills": req_list,
                "preferred_skills": pref_list,
                "minimum_experience": min_exp,
                "education_requirement": edu_req
            }
            new_id = db.save_job_description(job_record)
            st.success(f"🎉 Job '{job_title}' successfully saved with ID #{new_id}!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: Import from Dataset 2 ---
with tab_dataset2:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<div class='panel-header'>Search & Import from Dataset 2 (1.74 GB Catalog)</div>", unsafe_allow_html=True)

    c_srch, c_cur = st.columns([1.5, 1])
    with c_srch:
        srch_query = st.text_input("Live Search Dataset 2 by Keyword / Role:", placeholder="e.g. Data Scientist, Web Developer, Java...")
    with c_cur:
        curated_jobs = dataset_loader.load_curated_jobs()
        curated_names = [f"{j['job_title']} ({j.get('role', '')})" for j in curated_jobs]
        preset_choice = st.selectbox("Or Pick from Curated Role Catalog:", ["-- Select Preset --"] + curated_names)

    selected_import_job = None
    if preset_choice and preset_choice != "-- Select Preset --":
        idx = curated_names.index(preset_choice)
        selected_import_job = curated_jobs[idx]
    elif srch_query:
        with st.spinner("Streaming search across Dataset 2..."):
            matched_jobs = dataset_loader.search_jobs(srch_query, limit=10)
            if matched_jobs:
                st.write(f"Found **{len(matched_jobs)} matching postings** in Dataset 2:")
                opt_map = {f"{j['job_title']} at {j.get('company', 'Enterprise')} — {j.get('role', '')}": j for j in matched_jobs}
                picked_srch = st.selectbox("Select posting to preview:", list(opt_map.keys()))
                selected_import_job = opt_map[picked_srch]
            else:
                st.warning("No matching roles found.")

    if selected_import_job:
        st.markdown("---")
        st.markdown(f"### Preview: {selected_import_job['job_title']}")
        st.markdown(f"**Company:** {selected_import_job.get('company', 'Enterprise Tech')}")
        st.markdown(f"**Experience Requirement:** {selected_import_job.get('experience', '2 to 5 Years')}")
        st.markdown(f"**Documented Skills:** {selected_import_job.get('skills', '')}")
        st.markdown(f"**Responsibilities:** {selected_import_job.get('responsibilities', '')}")

        if st.button("📥 Import This Role to Active Database", type="primary"):
            parsed = job_parser.parse_job(
                title=selected_import_job["job_title"],
                description=selected_import_job.get("description", "") or selected_import_job.get("skills", ""),
                company=selected_import_job.get("company", "Enterprise")
            )
            parsed["minimum_experience"] = job_parser.extract_minimum_experience(selected_import_job.get("experience", ""))
            imported_id = db.save_job_description(parsed)
            st.success(f"🎉 Successfully imported '{selected_import_job['job_title']}' as Job #{imported_id}!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: Manage Saved Jobs ---
with tab_manage:
    saved_list = db.get_all_job_descriptions()
    if not saved_list:
        st.info("No saved job descriptions found.")
    else:
        for j in saved_list:
            with st.expander(f"📌 #{j['job_id']} — {j['job_title']} ({j.get('company_name', 'Confidential')})", expanded=False):
                st.markdown(f"**Created Date:** {j.get('created_at', 'Recently')}")
                st.markdown(f"**Experience Required:** {j.get('minimum_experience', 0):.1f} Years")
                st.markdown(f"**Education:** {j.get('education_requirement', 'Any')}")
                
                st.markdown("**Required Skills:**")
                st.markdown(render_skill_badges(j.get("required_skills", []), "matched"), unsafe_allow_html=True)
                
                if j.get("preferred_skills"):
                    st.markdown("<br>**Preferred Skills:**", unsafe_allow_html=True)
                    st.markdown(render_skill_badges(j.get("preferred_skills", []), "preferred"), unsafe_allow_html=True)

                st.markdown("<br>**Description:**", unsafe_allow_html=True)
                st.write(j.get("description", "")[:400] + ("..." if len(j.get("description", "")) > 400 else ""))

                col_del, _ = st.columns([1, 4])
                with col_del:
                    if st.button(f"🗑️ Delete Requisition #{j['job_id']}", key=f"del_{j['job_id']}"):
                        db.delete_job_description(j["job_id"])
                        st.success(f"Job #{j['job_id']} deleted!")
                        st.rerun()
