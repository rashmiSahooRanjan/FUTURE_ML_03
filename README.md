# 🎯 TalentRank AI — AI-Powered Resume Intelligence & Candidate Ranking Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E.svg?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![NLP](https://img.shields.io/badge/NLP-NLTK%20%7C%20spaCy-green.svg)](https://www.nltk.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-emerald.svg)]()

> **TalentRank AI** is an enterprise-grade, explainable recruitment intelligence platform built with Python, Natural Language Processing (NLP), Scikit-learn, and Streamlit. It parses multiple resume formats (PDF, DOCX, TXT), extracts technical competencies, benchmarks candidates against complex job descriptions, computes multi-factor compatibility scores, and generates audit-ready PDF/CSV dossiers.

---

## 📌 Table of Contents
1. [Project Overview](#-project-overview)
2. [Problem Statement & Objectives](#-problem-statement--objectives)
3. [Key Features](#-key-features)
4. [Technology Stack](#-technology-stack)
5. [System Architecture](#-system-architecture)
6. [Machine Learning & NLP Methodology](#-machine-learning--nlp-methodology)
7. [Mathematical Candidate Scoring Model](#-mathematical-candidate-scoring-model)
8. [Connected Datasets](#-connected-datasets)
9. [Project Directory Structure](#-project-directory-structure)
10. [Installation & Setup](#-installation--setup)
11. [Execution & Local Deployment](#-execution--local-deployment)
12. [Streamlit Community Cloud Deployment](#-streamlit-community-cloud-deployment)
13. [Ethical AI & Bias Mitigation](#-ethical-ai--bias-mitigation)
14. [Limitations & Future Roadmap](#-limitations--future-roadmap)
15. [License & Credits](#-license--credits)

---

## 🌟 Project Overview
Traditional applicant tracking systems (ATS) rely on rigid keyword searches that frequently discard qualified candidates or succumb to keyword-stuffing hacks. **TalentRank AI** bridges this gap by combining **TF-IDF vector semantics**, **boundary-aware NLP skill extraction**, **experience alignment**, and **explainable AI (XAI)** decision support.

The application operates **100% locally** without requiring expensive third-party AI APIs (OpenAI, Gemini, Claude).

---

## 🎯 Problem Statement & Objectives
- **Recruiter Fatigue:** Recruiters spend an average of 6–8 seconds per resume, leading to oversight and cognitive exhaustion.
- **Syntactic Keyword Blindness:** Keyword matchers miss synonymous tech terms (e.g., *ML* vs *Machine Learning*, *K8s* vs *Kubernetes*, *JS* vs *JavaScript*).
- **Opaque Scoring:** Most commercial screening engines fail to explain *why* a candidate received a particular ranking.
- **Objectives:**
  1. Automated, high-fidelity text extraction from PDF, DOCX, and TXT documents.
  2. Multi-tier skill extraction across 7 major technology taxonomy categories.
  3. Contextual TF-IDF cosine similarity vectorization.
  4. Explainable candidate scoring with dynamic recruiter weight control.
  5. Interactive visual analytics, side-by-side comparison, and PDF dossier generation.

---

## 🚀 Key Features

| Module | Core Functionality |
|---|---|
| **📊 Executive Dashboard** | Real-time KPI metric cards, score distribution donut, top candidate rankings, and skill demand heatmaps. |
| **📄 Resume Screening** | Multi-file uploader (PDF/DOCX/TXT), duplicate hash checker, and instant 1-click loading from **Dataset 1** (24 industry domains). |
| **🏆 Candidate Ranking** | Dynamic leaderboard with multi-criteria tie-breaking, score and experience filtering, and side-by-side comparison of up to 5 candidates. |
| **👤 Candidate Explorer** | Deep candidate dossier, contact extraction (LinkedIn, GitHub, Email, Phone), multi-dimensional radar scorecards, and recruiter notes management. |
| **🔍 Skill Gap Analysis** | Matrix comparing required vs detected skills, category coverage percentages, and targeted technical interview question generation. |
| **📋 Job Description Manager** | Requisition manager with automatic skill segmentation (Mandatory vs Preferred) and streaming search across **Dataset 2** (1.74 GB catalog). |
| **📈 Analytics & Reports** | Statistical cohort distributions, candidate skill frequency graphs, and downloadable PDF/CSV reports. |
| **📜 Screening History** | Persistent SQLite screening session audit logs with cohort comparison and session restoration. |
| **ℹ️ About & Ethics** | Comprehensive documentation of mathematical scoring formulas, NLP architectures, and non-discriminatory ethical AI practices. |

---

## 🛠️ Technology Stack

- **Core Backend:** Python 3.10+
- **Frontend / UI:** Streamlit with Custom Enterprise CSS (Plus Jakarta Sans typography, sleek card layouts, dynamic pills)
- **Machine Learning:** Scikit-learn (`TfidfVectorizer`, `cosine_similarity`)
- **Natural Language Processing:** NLTK (`stopwords`, `lemmatizer`, boundary-aware regex)
- **Document Parsers:** PyMuPDF (`fitz`), `python-docx`
- **Data Engineering:** Pandas, NumPy
- **Visualizations:** Plotly Interactive Graphs (`go.Scatterpolar`, `go.Bar`, `px.pie`, `px.histogram`)
- **Reporting:** ReportLab (Vector-quality PDF dossier generation)
- **Database:** SQLite (ACID compliant with parameterized queries)
- **Quality Assurance:** Python Unittest (Automated test suite)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      TalentRank AI UI                       │
│      Streamlit SaaS Dashboard  •  Custom Enterprise CSS     │
└───────────────▲─────────────────────────────▲───────────────┘
                │                             │
    ┌───────────┴─────────────┐   ┌───────────┴─────────────┐
    │  Resume Ingestion Engine │   │   Job Requisition Engine │
    │  • PyMuPDF (PDF Parser) │   │   • Dataset 2 Streamer  │
    │  • python-docx (DOCX)   │   │   • Mandatory vs Pref.  │
    │  • SHA-256 Deduplication│   │   • Exp & Degree Parser │
    └───────────┬─────────────┘   └───────────┬─────────────┘
                │                             │
                ▼                             ▼
    ┌─────────────────────────────────────────────────────────┐
    │          NLP Preprocessing & Feature Extraction         │
    │  • Technical Token Protection (C++, C#, .NET, CI/CD)    │
    │  • 7-Category Skill Taxonomy & Alias Resolution Engine  │
    └───────────────────────────┬─────────────────────────────┘
                                │
                                ▼
    ┌─────────────────────────────────────────────────────────┐
    │              Multi-Factor Scoring Engine                │
    │  • TF-IDF Vectorization & Sublinear Cosine Similarity   │
    │  • Proportional Experience & Education Alignment        │
    │  • Keyword Relevance & Dynamic Recruiter Weighting      │
    └───────────────────────────┬─────────────────────────────┘
                                │
                                ▼
    ┌─────────────────────────────────────────────────────────┐
    │           Output, Explainability & Persistence          │
    │  • Multi-Tier Tie-Breaking Leaderboard                  │
    │  • Explainable AI (XAI) Natural Language Synthesis     │
    │  • SQLite Storage & ReportLab PDF Dossier Export        │
    └─────────────────────────────────────────────────────────┘
```

---

## 🧠 Machine Learning & NLP Methodology

### 1. NLP Preprocessing Pipeline
1. **HTML & Tag Stripping:** Purges markup from raw resume strings.
2. **Technical Symbol Preservation:** Preserves programming symbols (`C++`, `C#`, `.NET`, `Node.js`, `CI/CD`) through semantic token encapsulation prior to punctuation stripping.
3. **Boundary-Aware Regex Tokenization:** Word boundary validation prevents partial substring false-positives (e.g., isolated `C` language will not match inside words like `concept` or `accuracy`).
4. **Alias Resolution:** Standardizes technical variations (*ML* $\rightarrow$ *Machine Learning*, *K8s* $\rightarrow$ *Kubernetes*, *Postgres* $\rightarrow$ *PostgreSQL*).

### 2. TF-IDF & Cosine Similarity
Text is converted into numerical vectors across unigram and bigram token distributions with sublinear term-frequency scaling:

$$\text{Cosine Similarity} = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}} \times 100$$

---

## 📐 Mathematical Candidate Scoring Model

The final match score is a multi-dimensional composite score bounded between $0.0$ and $100.0$:

$$\text{Final Score} = (S_{\text{req}} \cdot w_{\text{req}}) + (\text{Sim}_{\text{tfidf}} \cdot w_{\text{sim}}) + (S_{\text{pref}} \cdot w_{\text{pref}}) + (\text{Exp} \cdot w_{\text{exp}}) + (\text{Edu} \cdot w_{\text{edu}}) + (\text{Key} \cdot w_{\text{key}})$$

### Default Weight Distribution:
- **Mandatory Skills Match ($S_{\text{req}}$):** $40\%$
- **TF-IDF Semantic Similarity ($\text{Sim}$):** $25\%$
- **Preferred Skills Match ($S_{\text{pref}}$):** $15\%$
- **Experience Compatibility ($\text{Exp}$):** $10\%$
- **Education Alignment ($\text{Edu}$):** $5\%$
- **Domain Keyword Relevance ($\text{Key}$):** $5\%$

### Recommendation Categorization:
- **$\ge 80.0\%$:** `Strong Match` (Meets critical tech prerequisites and high semantic alignment)
- **$65.0\% - 79.9\%$:** `Good Match` (Solid foundational competency with minor skill or experience gaps)
- **$45.0\% - 64.9\%$:** `Partial Match` (Cross-domain profile requiring upskilling or interview probe)
- **$< 45.0\%$:** `Needs Review` (Significant qualification divergence)

---

## 📦 Connected Datasets

The project natively integrates two Kaggle benchmark datasets located directly in `Dataset/`:

1. **Dataset 1 — Kaggle Resume Dataset (Sneha Anbhawal)**
   - **Path:** `Dataset/Dataset 1/`
   - **Files:** `Resume.csv` (56 MB) and `data/data/` (24 category directories of actual PDF resumes).
   - **Domains:** Information Technology, HR, Advocate, Accountant, Engineering, Finance, Aviation, Healthcare, Digital Media, etc.
   - **Integration:** 1-click batch loader in Resume Screening page.

2. **Dataset 2 — Kaggle Job Description Dataset (Ravindra Singh Rana)**
   - **Path:** `Dataset/Dataset 2/job_descriptions.csv` (1.74 GB)
   - **Features:** Real enterprise postings containing roles, required qualifications, minimum experience, and required skills.
   - **Integration:** Curated instant presets (30+ roles) and real-time streaming search in Job Manager.

---

## 📂 Project Directory Structure

```text
TalentRank-AI/
│
├── app.py                         # Main Streamlit Application Entrypoint
├── config.py                      # System Configuration, Constants & Weights
├── requirements.txt               # Pinned Python Dependencies
├── runtime.txt                    # Deployment Python Runtime
├── README.md                      # Comprehensive Architecture Documentation
├── .gitignore                     # Git Exclusion Rules
│
├── assets/
│   ├── custom.css                 # Enterprise SaaS CSS Theme
│   ├── logo.svg                   # Vector SVG Platform Brand Logo
│   └── custom.css                 # Responsive Design Rules
│
├── data/
│   ├── skills_dictionary.json     # 7-Category Skill Taxonomy & Alias Map
│   └── sample_data/
│       └── curated_jobs.json      # 30+ Pre-extracted Roles from Dataset 2
│
├── database/
│   ├── db.py                      # SQLite Transactional Database Manager
│   ├── schema.sql                 # SQL Schema (Candidates, Jobs, Sessions, Notes)
│   └── talentrank.db              # SQLite Database File
│
├── modules/
│   ├── resume_parser.py           # Multi-Format PDF/DOCX/TXT Parser
│   ├── text_preprocessing.py      # NLP Pipeline & Tokenizer
│   ├── skill_extractor.py         # Boundary-Aware Skill Extraction Engine
│   ├── job_parser.py              # Requisition & Mandatory/Preferred Segmenter
│   ├── similarity_engine.py       # TF-IDF Cosine Similarity Vectorizer
│   ├── scoring_engine.py          # Multi-Factor Weighted Evaluation Engine
│   ├── candidate_ranker.py        # Descending Leaderboard & Tie-Breaker
│   ├── skill_gap_analyzer.py      # Competency Gap Matrix & Coverage Analyzer
│   ├── explainability.py          # Explainable AI (XAI) Synthesis Module
│   └── report_generator.py        # ReportLab Vector PDF & CSV Generator
│
├── pages/
│   ├── 1_📊_Dashboard.py           # Analytics Dashboard & KPI Cards
│   ├── 2_📄_Resume_Screening.py    # Multi-Resume Upload & Batch Evaluation
│   ├── 3_🏆_Candidate_Ranking.py   # Interactive Leaderboard & 5-Way Comparison
│   ├── 4_👤_Candidate_Explorer.py  # Profile Dossier, Radar & Recruiter Notes
│   ├── 5_🔍_Skill_Gap_Analysis.py  # Matrix View & Technical Interview Prompts
│   ├── 6_📋_Job_Description_Manager.py # Requisition Editor & Dataset 2 Streamer
│   ├── 7_📈_Analytics_Reports.py   # Cohort Statistics & PDF Download
│   ├── 8_📜_Screening_History.py   # Historical Audit Log & Session Comparison
│   └── 9_ℹ️_About.py               # Technical Specifications & Ethics Framework
│
├── utils/
│   ├── validators.py              # File Size, Type, and Weight Sum Validators
│   ├── helpers.py                 # UI Cards, Pills & Plotly Visualizations
│   ├── export_utils.py            # CSV and Excel Data Streamers
│   └── dataset_loader.py          # Dataset 1 & Dataset 2 Integration Bridge
│
└── tests/
    ├── test_resume_parser.py      # Resume Parser Tests
    ├── test_skill_extractor.py    # Skill Extraction & Boundary Tests
    ├── test_scoring_engine.py     # Evaluation & Weight Sum Tests
    └── test_candidate_ranker.py   # Ranking & Tie-Breaker Tests
```

---

## 💻 Installation & Setup

### Prerequisites
- Python 3.10+ installed
- Git installed

### 1. Clone or Open Workspace
```bash
cd "d:\Future In tern Project\Project - 3"
```

### 2. Create and Activate Virtual Environment (Optional but Recommended)
```bash
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Execution & Local Deployment

To run the complete platform locally:

```bash
streamlit run app.py
```

The Streamlit development server will launch at:
```
Local URL: http://localhost:8501
Network URL: http://<your-ip>:8501
```

---

## 🧪 Running Automated Tests

Run the full automated test suite covering all modules:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Expected output:
```text
...............
----------------------------------------------------------------------
Ran 15 tests in 2.654s

OK
```

---

## ☁️ Streamlit Community Cloud Deployment

1. **Commit Project to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "feat: complete TalentRank AI platform"
   git branch -M main
   git remote add origin https://github.com/<your-username>/TalentRank-AI.git
   git push -u origin main
   ```
2. **Deploy on Streamlit Cloud:**
   - Navigate to [share.streamlit.io](https://share.streamlit.io/)
   - Connect your GitHub repository.
   - Set **Main file path:** `app.py`.
   - Click **Deploy!**

---

## ⚖️ Ethical AI & Bias Mitigation
TalentRank AI is strictly built to comply with modern algorithmic hiring regulations:
- **Zero Demographic Bias:** Protected characteristics including candidate age, gender, ethnicity, religion, caste, nationality, disability, and photographs are intentionally omitted from parsing and scoring logic.
- **Explainability as a Standard:** Every single score is transparently decomposed into its component parts.
- **Decision-Support Guardrails:** Rankings are presented to human recruiters as advisory decision-support signals rather than autonomous hiring or rejection decisions.

---

## 🔮 Future Enhancements
- [ ] Integration of locally-hosted Sentence-Transformers (`all-MiniLM-L6-v2`) for dense vector semantic embeddings.
- [ ] Multi-lingual resume support across German, Spanish, French, and Hindi.
- [ ] Automated calendar and email interview scheduling triggers.
- [ ] Integration with cloud databases (PostgreSQL, Supabase) for multi-tenant enterprise deployments.

---

## 📄 License & Credits
Developed as an advanced Machine Learning & NLP intern project. Distributed under the MIT License.
