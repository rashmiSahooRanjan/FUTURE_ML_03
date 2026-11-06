"""
TalentRank AI — Resume Screening Module
Uploads and parses multiple PDF/DOCX/TXT resumes, integrates Dataset 1 and Dataset 2,
and runs the multi-factor scoring engine with configurable weights.
"""

import streamlit as st
from pathlib import Path
from database.db import db
from modules.resume_parser import resume_parser
from modules.job_parser import job_parser
from modules.scoring_engine import scoring_engine
from modules.candidate_ranker import candidate_ranker
from utils.helpers import load_custom_css, render_hero_banner
from utils.validators import validator
from utils.dataset_loader import dataset_loader
from config import DEFAULT_WEIGHTS

st.set_page_config(page_title="Resume Screening — TalentRank AI", page_icon="📄", layout="wide")
load_custom_css()

render_hero_banner(
    title="Resume Screening Engine",
    subtitle="Upload multiple candidate resumes or import directly from Dataset 1. Match against target job specifications using multi-factor NLP intelligence.",
    badge_text="Batch Screening & Parsing"
)

# Step 1: Select Target Job Description
st.markdown("### 1️⃣ Target Job Description")

saved_jobs = db.get_all_job_descriptions()
curated_jobs = dataset_loader.load_curated_jobs()

job_source = st.radio(
    "Choose Job Source:",
    ["Select from Database", "Import from Dataset 2 (Job Catalog)", "Create New Job Description"],
    horizontal=True
)

active_job = None

if job_source == "Select from Database":
    if saved_jobs:
        job_options = {f"{j['job_title']} ({j.get('company_name', 'Confidential')})": j for j in saved_jobs}
        selected_title = st.selectbox("Select saved job role:", list(job_options.keys()))
        active_job = job_options[selected_title]
    else:
        st.warning("No saved job descriptions found. Please import from Dataset 2 or create a new one.")

elif job_source == "Import from Dataset 2 (Job Catalog)":
    if curated_jobs:
        curated_options = {f"{j['job_title']} — {j.get('role', '')}": j for j in curated_jobs}
        selected_curated = st.selectbox("Select real-world role from Dataset 2:", list(curated_options.keys()))
        selected_raw = curated_options[selected_curated]

        # Parse and save to DB
        with st.expander("Preview Selected Job Specifications", expanded=True):
            st.markdown(f"**Job Title:** {selected_raw['job_title']}")
            st.markdown(f"**Company:** {selected_raw.get('company', 'Enterprise Tech')}")
            st.markdown(f"**Experience Requirement:** {selected_raw.get('experience', '2 to 5 Years')}")
            st.markdown(f"**Required Skills:** {selected_raw.get('skills', '')}")
            st.caption(f"**Description:** {selected_raw.get('description', '')[:300]}...")

        # Construct active job
        parsed_job = job_parser.parse_job(
            title=selected_raw["job_title"],
            description=selected_raw.get("description", "") or selected_raw.get("skills", ""),
            company=selected_raw.get("company", "Enterprise Tech")
        )
        parsed_job["minimum_experience"] = job_parser.extract_minimum_experience(selected_raw.get("experience", ""))
        active_job = parsed_job
    else:
        st.error("Dataset 2 jobs could not be loaded.")

elif job_source == "Create New Job Description":
    with st.expander("Quick Create Job Description", expanded=True):
        new_title = st.text_input("Job Title", value="Senior Python & ML Engineer")
        new_company = st.text_input("Company Name", value="Antigravity Technologies")
        new_desc = st.text_area(
            "Job Description (paste full requirements)",
            value="We are seeking an experienced Python Developer with strong background in Machine Learning, Flask, SQL, Docker, and REST APIs. Minimum 3 years of experience required with a Bachelor's degree in Computer Science."
        )
        if st.button("Parse and Use Job Description"):
            active_job = job_parser.parse_job(new_title, new_desc, new_company)
            jid = db.save_job_description(active_job)
            active_job["job_id"] = jid
            st.success(f"Job '{new_title}' saved and active!")

st.markdown("<br>", unsafe_allow_html=True)

# Step 2: Scoring Weights Configuration
st.markdown("### 2️⃣ Evaluation Weights Configuration")
with st.expander("⚙️ Customize Evaluation Weights (Must sum to 100%)", expanded=False):
    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        w_req = st.slider("Required Skills Match (%)", 0, 100, int(DEFAULT_WEIGHTS["required_skills"] * 100), 5)
        w_sim = st.slider("TF-IDF Text Similarity (%)", 0, 100, int(DEFAULT_WEIGHTS["similarity"] * 100), 5)
    with col_w2:
        w_pref = st.slider("Preferred Skills Match (%)", 0, 100, int(DEFAULT_WEIGHTS["preferred_skills"] * 100), 5)
        w_exp = st.slider("Experience Alignment (%)", 0, 100, int(DEFAULT_WEIGHTS["experience"] * 100), 5)
    with col_w3:
        w_edu = st.slider("Education Alignment (%)", 0, 100, int(DEFAULT_WEIGHTS["education"] * 100), 5)
        w_key = st.slider("Keyword Relevance (%)", 0, 100, int(DEFAULT_WEIGHTS["keyword"] * 100), 5)

    total_weight = w_req + w_sim + w_pref + w_exp + w_edu + w_key
    if total_weight != 100:
        st.error(f"⚠️ Total weights must equal 100%. Currently: {total_weight}%")
    else:
        st.success("✅ Weights validated: 100% total.")

    custom_weights = {
        "required_skills": w_req / 100.0,
        "similarity": w_sim / 100.0,
        "preferred_skills": w_pref / 100.0,
        "experience": w_exp / 100.0,
        "education": w_edu / 100.0,
        "keyword": w_key / 100.0
    }
    scoring_engine.set_weights(custom_weights)

st.markdown("<br>", unsafe_allow_html=True)

# Step 3: Resumes Input (Upload or Load from Dataset 1)
st.markdown("### 3️⃣ Candidate Resumes Input")

tab_upload, tab_dataset1 = st.tabs(["📤 Upload Custom Resumes", "📦 Load from Dataset 1 (24 Domains)"])

uploaded_files_data = []

with tab_upload:
    uploaded_files = st.file_uploader(
        "Upload candidate resumes (PDF, DOCX, TXT):",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )
    if uploaded_files:
        st.info(f"Selected {len(uploaded_files)} file(s) for screening.")
        for uf in uploaded_files:
            file_bytes = uf.read()
            valid, err = validator.validate_file(uf.name, len(file_bytes))
            if valid:
                uploaded_files_data.append({"filename": uf.name, "bytes": file_bytes})
            else:
                st.warning(f"{uf.name}: {err}")

with tab_dataset1:
    categories = dataset_loader.get_dataset1_categories()
    if categories:
        c_cat, c_cnt = st.columns([2, 1])
        with c_cat:
            selected_cat = st.selectbox("Select Domain Category from Dataset 1:", categories, index=categories.index("INFORMATION-TECHNOLOGY") if "INFORMATION-TECHNOLOGY" in categories else 0)
        with c_cnt:
            num_resumes = st.slider("Number of Resumes to Load:", min_value=3, max_value=25, value=8)

        if st.button("📥 Load Resumes from Dataset 1", type="secondary"):
            with st.spinner(f"Loading {num_resumes} real PDF resumes from category '{selected_cat}'..."):
                d1_candidates = dataset_loader.load_resumes_from_pdfs(selected_cat, limit=num_resumes)
                if not d1_candidates:
                    # CSV fallback
                    d1_candidates = dataset_loader.load_resumes_from_csv(selected_cat, limit=num_resumes)

                st.session_state["dataset1_loaded"] = d1_candidates
                st.success(f"Successfully loaded and parsed {len(d1_candidates)} resumes from Dataset 1!")

    if "dataset1_loaded" in st.session_state and st.session_state["dataset1_loaded"]:
        st.write(f"**Loaded from Dataset 1:** {len(st.session_state['dataset1_loaded'])} candidates ready for evaluation.")

st.markdown("<br>", unsafe_allow_html=True)

# Step 4: Run Batch Screening Engine
if st.button("🚀 Start Screening & Candidate Ranking", type="primary", use_container_width=True):
    if not active_job:
        st.error("Please select or create an active target Job Description first.")
        st.stop()

    candidates_to_screen = []

    # 1. Process custom uploaded files
    if uploaded_files_data:
        progress_bar = st.progress(0, text="Parsing uploaded resumes...")
        for idx, uf in enumerate(uploaded_files_data):
            progress_bar.progress((idx + 1) / len(uploaded_files_data), text=f"Parsing {uf['filename']}...")
            res = resume_parser.parse_resume(uf["filename"], uf["bytes"])
            if res.get("success"):
                candidates_to_screen.append(res)
            else:
                st.warning(f"Skipping {uf['filename']}: {res.get('error')}")

    # 2. Add Dataset 1 loaded candidates
    if "dataset1_loaded" in st.session_state and st.session_state["dataset1_loaded"]:
        candidates_to_screen.extend(st.session_state["dataset1_loaded"])

    if not candidates_to_screen:
        st.error("No valid resumes provided. Please upload resumes or load from Dataset 1.")
        st.stop()

    # Ensure job is saved in SQLite
    if "job_id" not in active_job or not active_job["job_id"]:
        jid = db.save_job_description(active_job)
        active_job["job_id"] = jid

    with st.spinner(f"Scoring {len(candidates_to_screen)} candidates against '{active_job['job_title']}'..."):
        # Create screening session
        session_id = db.create_screening_session(
            job_id=active_job["job_id"],
            total_resumes=len(candidates_to_screen),
            processed_resumes=len(candidates_to_screen)
        )

        scored_candidates = []
        for cand in candidates_to_screen:
            # Save candidate to SQLite
            cid = db.save_candidate(cand)
            cand["candidate_id"] = cid

            # Multi-component score
            score_res = scoring_engine.score_candidate(cand, active_job)
            score_res["session_id"] = session_id
            db.save_screening_result(score_res)
            scored_candidates.append(score_res)

        # Rank candidates
        ranked = candidate_ranker.rank_candidates(scored_candidates)
        st.session_state["last_ranked"] = ranked
        st.session_state["active_session_id"] = session_id

    st.success(f"🎉 Successfully screened and ranked {len(ranked)} candidates for session #{session_id}!")

    # Direct action button to View Ranking
    col_go, _ = st.columns([1, 2])
    with col_go:
        if st.button("View Candidate Leaderboard & Rankings →", type="primary", use_container_width=True):
            st.switch_page("pages/3_🏆_Candidate_Ranking.py")
