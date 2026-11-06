"""
TalentRank AI — About & System Architecture Module
Detailed technical specifications, ML methodologies, mathematical formulations,
and ethical AI recruiting standards.
"""

import streamlit as st
from utils.helpers import load_custom_css, render_hero_banner

st.set_page_config(page_title="About Platform — TalentRank AI", page_icon="ℹ️", layout="wide")
load_custom_css()

render_hero_banner(
    title="About TalentRank AI",
    subtitle="Next-generation transparent resume intelligence, NLP text extraction, and multi-factor ranking architecture.",
    badge_text="System Architecture & Ethics"
)

tab_overview, tab_ml, tab_ethics, tab_datasets = st.tabs([
    "🏛️ System Architecture",
    "🧠 ML & Mathematical Formulations",
    "⚖️ Ethical AI & Bias Mitigation",
    "📦 Connected Datasets"
])

# --- TAB 1: System Architecture ---
with tab_overview:
    st.markdown("""
    ### 🏗️ End-to-End System Architecture
    TalentRank AI is engineered as a modular, production-grade recruitment intelligence platform:
    """)

    st.markdown("""
    ```
    ┌──────────────────────┐      ┌─────────────────────────┐
    │  Resume Ingestion    │      │  Job Description Module │
    │  • PDF (PyMuPDF)     │      │  • Dataset 2 Streamer   │
    │  • DOCX (python-docx)│      │  • Role Requisition     │
    │  • TXT Standard      │      │  • Skill Segmenter      │
    └──────────┬───────────┘      └────────────┬────────────┘
               │                               │
               ▼                               ▼
    ┌───────────────────────────────────────────────────────┐
    │            NLP Preprocessing & Feature Extraction     │
    │  • Tokenization & Boundary-Aware Regex               │
    │  • Technical Symbol Protection (C++, C#, .NET, CI/CD) │
    │  • Configurable Skill Taxonomy & Alias Resolution    │
    └──────────────────────────┬────────────────────────────┘
                               │
                               ▼
    ┌───────────────────────────────────────────────────────┐
    │             Multi-Factor Scoring Engine               │
    │  • TF-IDF Vectorization & Sublinear Cosine Similarity │
    │  • Mandatory & Preferred Skill Coverage               │
    │  • Experience Alignment & Degree Compatibility        │
    └──────────────────────────┬────────────────────────────┘
                               │
                               ▼
    ┌───────────────────────────────────────────────────────┐
    │        Explainable AI & Candidate Ranking             │
    │  • Multi-Tier Tie-Breaking Leaderboard                │
    │  • Transparent Natural Language Reasoning             │
    │  • SQLite Persistence & ReportLab PDF Dossiers        │
    └───────────────────────────────────────────────────────┘
    ```
    """)

    st.markdown("""
    #### 🛠️ Technology Stack
    - **Language:** Python 3.10+
    - **Frontend:** Streamlit with Custom Enterprise CSS
    - **Machine Learning & NLP:** Scikit-learn, NLTK, spaCy-ready architecture
    - **Document Extraction:** PyMuPDF (fitz), python-docx
    - **Visualizations:** Plotly Interactive Graphs
    - **Report Generation:** ReportLab (vector-quality PDF rendering)
    - **Persistence:** SQLite with ACID transactional guarantees
    """)

# --- TAB 2: ML & Formulations ---
with tab_ml:
    st.markdown("### 📐 Mathematical Formulations & Scoring Methodology")

    st.markdown("""
    #### 1. TF-IDF Cosine Similarity
    Text representations are transformed into sparse term frequency-inverse document frequency vectors across unigrams and bigrams:
    """)

    st.latex(r"\text{Cosine Similarity} = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}} \times 100")

    st.markdown("""
    #### 2. Multi-Factor Weighted Scoring Model
    Unlike simplistic keyword matchers, TalentRank AI computes a multi-dimensional weighted score:
    """)

    st.latex(r"\text{Final Score} = (S_{\text{req}} \cdot w_{\text{req}}) + (\text{Sim}_{\text{tfidf}} \cdot w_{\text{sim}}) + (S_{\text{pref}} \cdot w_{\text{pref}}) + (\text{Exp} \cdot w_{\text{exp}}) + (\text{Edu} \cdot w_{\text{edu}}) + (\text{Key} \cdot w_{\text{key}})")

    st.markdown("""
    | Evaluation Dimension | Default Weight | Formula / Source |
    |---|:---:|---|
    | **Required Skills Match ($S_{\text{req}}$)** | 40% | $(\text{Matched Required} / \text{Total Required}) \times 100$ |
    | **TF-IDF Text Similarity ($\text{Sim}$)** | 25% | Cosine similarity between clean resume & job vectors |
    | **Preferred Skills Match ($S_{\text{pref}}$)** | 15% | $(\text{Matched Preferred} / \text{Total Preferred}) \times 100$ |
    | **Experience Alignment ($\text{Exp}$)** | 10% | $\min(100, (\text{Candidate Exp} / \text{Required Exp}) \times 100)$ |
    | **Education Compatibility ($\text{Edu}$)** | 5% | Degree level alignment (Ph.D., Master's, Bachelor's) |
    | **Domain Keyword Relevance ($\text{Key}$)** | 5% | Overlap of top 25 high-frequency job keywords in resume |
    """)

# --- TAB 3: Ethical AI ---
with tab_ethics:
    st.markdown("""
    ### ⚖️ Ethical AI & Bias Mitigation Framework
    TalentRank AI is strictly designed around responsible algorithmic hiring principles:

    1. **Strictly Non-Discriminatory:**
       - Protected characteristics including **age, gender, religion, caste, nationality, disability, and photographs are never parsed, indexed, or factored into scoring**.
    2. **Explainable AI (XAI):**
       - The system avoids "black-box" neural scoring. Every score has an explicit, auditable breakdown showing how each component contributed to the final rank.
    3. **Missing Data Normalization:**
       - Missing information (e.g., unmentioned graduation year or unstated phone number) is treated with neutral baselines rather than severe negative penalties.
    4. **Decision-Support Orientation:**
       - The platform produces **recommendation categories** (*Strong Match*, *Good Match*, *Partial Match*, *Needs Review*) as decision support for human recruiters, not automated rejection verdicts.
    """)

# --- TAB 4: Datasets ---
with tab_datasets:
    st.markdown("""
    ### 📦 Connected Kaggle Datasets
    This project natively incorporates two comprehensive open-source datasets located in `Dataset/`:

    #### 1. Resume Dataset (Sneha Anbhawal)
    - **Local Path:** `Dataset/Dataset 1/`
    - **Resume.csv:** 56 MB with extracted resumes across 24 job categories.
    - **PDF Documents:** 24 dedicated category directories (`data/data/`) containing thousands of original PDF resumes.
    - **Categories:** Information Technology, HR, Advocate, Accountant, Engineering, Finance, Aviation, Healthcare, Digital Media, etc.

    #### 2. Job Description Dataset (Ravindra Singh Rana)
    - **Local Path:** `Dataset/Dataset 2/job_descriptions.csv`
    - **Size:** 1.74 GB enterprise job description catalog.
    - **Features:** Roles, minimum experience, qualifications, salary ranges, benefits, required skills, and responsibilities.
    """)

