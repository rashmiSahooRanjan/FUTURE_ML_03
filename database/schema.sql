-- TalentRank AI SQLite Database Schema

CREATE TABLE IF NOT EXISTS candidates (
    candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_name TEXT,
    email TEXT,
    phone TEXT,
    location TEXT,
    resume_filename TEXT,
    resume_hash TEXT UNIQUE,
    extracted_text TEXT,
    cleaned_text TEXT,
    extracted_skills TEXT, -- JSON array
    education TEXT,
    experience REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_descriptions (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title TEXT NOT NULL,
    company_name TEXT,
    description TEXT NOT NULL,
    required_skills TEXT, -- JSON array
    preferred_skills TEXT, -- JSON array
    minimum_experience REAL DEFAULT 0,
    education_requirement TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS screening_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    total_resumes INTEGER DEFAULT 0,
    processed_resumes INTEGER DEFAULT 0,
    screening_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES job_descriptions (job_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS screening_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    candidate_id INTEGER,
    final_score REAL,
    skill_score REAL,
    similarity_score REAL,
    experience_score REAL,
    education_score REAL,
    keyword_score REAL,
    preferred_skill_score REAL,
    matched_skills TEXT, -- JSON array
    missing_skills TEXT, -- JSON array
    recommendation TEXT,
    FOREIGN KEY (session_id) REFERENCES screening_sessions (session_id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER,
    session_id INTEGER,
    notes TEXT,
    screening_status TEXT DEFAULT 'Under Review',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES screening_sessions (session_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_candidate_hash ON candidates (resume_hash);
CREATE INDEX IF NOT EXISTS idx_screening_session ON screening_results (session_id);
CREATE INDEX IF NOT EXISTS idx_candidate_notes ON candidate_notes (candidate_id, session_id);

