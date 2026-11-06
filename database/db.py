"""
Database Manager for TalentRank AI
Provides robust, thread-safe SQLite operations for candidates, job descriptions,
screening sessions, scoring results, and recruiter notes.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from config import DB_PATH, DATABASE_DIR

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = str(db_path or DB_PATH)
        self._ensure_db_dir()
        self.init_db()

    def _ensure_db_dir(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        schema_path = DATABASE_DIR / "schema.sql"
        if not schema_path.exists():
            return
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        with self.get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    # --- Candidates CRUD ---
    def save_candidate(self, candidate_data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO candidates (
            candidate_name, email, phone, location, resume_filename,
            resume_hash, extracted_text, cleaned_text, extracted_skills,
            education, experience
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(resume_hash) DO UPDATE SET
            candidate_name = excluded.candidate_name,
            email = excluded.email,
            phone = excluded.phone,
            location = excluded.location,
            extracted_text = excluded.extracted_text,
            cleaned_text = excluded.cleaned_text,
            extracted_skills = excluded.extracted_skills,
            education = excluded.education,
            experience = excluded.experience
        RETURNING candidate_id;
        """
        skills_json = json.dumps(candidate_data.get("extracted_skills", []))
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                candidate_data.get("candidate_name", "Unknown Candidate"),
                candidate_data.get("email", "Not Found"),
                candidate_data.get("phone", "Not Found"),
                candidate_data.get("location", "Not Found"),
                candidate_data.get("resume_filename", ""),
                candidate_data.get("resume_hash", ""),
                candidate_data.get("extracted_text", ""),
                candidate_data.get("cleaned_text", ""),
                skills_json,
                candidate_data.get("education", "Not Found"),
                candidate_data.get("experience", 0.0)
            ))
            row = cursor.fetchone()
            conn.commit()
            return row["candidate_id"] if row else cursor.lastrowid

    def get_candidate(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM candidates WHERE candidate_id = ?", (candidate_id,))
            row = cursor.fetchone()
            if row:
                res = dict(row)
                res["extracted_skills"] = json.loads(res.get("extracted_skills") or "[]")
                return res
            return None

    def get_candidate_by_hash(self, resume_hash: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM candidates WHERE resume_hash = ?", (resume_hash,))
            row = cursor.fetchone()
            if row:
                res = dict(row)
                res["extracted_skills"] = json.loads(res.get("extracted_skills") or "[]")
                return res
            return None

    def get_all_candidates(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM candidates ORDER BY candidate_id DESC")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["extracted_skills"] = json.loads(item.get("extracted_skills") or "[]")
                results.append(item)
            return results

    # --- Job Descriptions CRUD ---
    def save_job_description(self, job_data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO job_descriptions (
            job_title, company_name, description, required_skills,
            preferred_skills, minimum_experience, education_requirement
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        req_json = json.dumps(job_data.get("required_skills", []))
        pref_json = json.dumps(job_data.get("preferred_skills", []))
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                job_data.get("job_title", "Untitled Role"),
                job_data.get("company_name", "Confidential"),
                job_data.get("description", ""),
                req_json,
                pref_json,
                float(job_data.get("minimum_experience", 0.0)),
                job_data.get("education_requirement", "Any Degree")
            ))
            conn.commit()
            return cursor.lastrowid

    def update_job_description(self, job_id: int, job_data: Dict[str, Any]) -> bool:
        query = """
        UPDATE job_descriptions SET
            job_title = ?, company_name = ?, description = ?,
            required_skills = ?, preferred_skills = ?,
            minimum_experience = ?, education_requirement = ?
        WHERE job_id = ?
        """
        req_json = json.dumps(job_data.get("required_skills", []))
        pref_json = json.dumps(job_data.get("preferred_skills", []))
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                job_data.get("job_title", "Untitled Role"),
                job_data.get("company_name", "Confidential"),
                job_data.get("description", ""),
                req_json,
                pref_json,
                float(job_data.get("minimum_experience", 0.0)),
                job_data.get("education_requirement", "Any Degree"),
                job_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_job_description(self, job_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM job_descriptions WHERE job_id = ?", (job_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_job_description(self, job_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM job_descriptions WHERE job_id = ?", (job_id,))
            row = cursor.fetchone()
            if row:
                res = dict(row)
                res["required_skills"] = json.loads(res.get("required_skills") or "[]")
                res["preferred_skills"] = json.loads(res.get("preferred_skills") or "[]")
                return res
            return None

    def get_all_job_descriptions(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM job_descriptions ORDER BY job_id DESC")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["required_skills"] = json.loads(item.get("required_skills") or "[]")
                item["preferred_skills"] = json.loads(item.get("preferred_skills") or "[]")
                results.append(item)
            return results

    # --- Screening Sessions & Results ---
    def create_screening_session(self, job_id: int, total_resumes: int, processed_resumes: int) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO screening_sessions (job_id, total_resumes, processed_resumes) VALUES (?, ?, ?)",
                (job_id, total_resumes, processed_resumes)
            )
            conn.commit()
            return cursor.lastrowid

    def save_screening_result(self, result_data: Dict[str, Any]) -> int:
        query = """
        INSERT INTO screening_results (
            session_id, candidate_id, final_score, skill_score,
            similarity_score, experience_score, education_score,
            keyword_score, preferred_skill_score, matched_skills,
            missing_skills, recommendation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        matched_json = json.dumps(result_data.get("matched_skills", []))
        missing_json = json.dumps(result_data.get("missing_skills", []))
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                result_data.get("session_id"),
                result_data.get("candidate_id"),
                float(result_data.get("final_score", 0.0)),
                float(result_data.get("skill_score", 0.0)),
                float(result_data.get("similarity_score", 0.0)),
                float(result_data.get("experience_score", 0.0)),
                float(result_data.get("education_score", 0.0)),
                float(result_data.get("keyword_score", 0.0)),
                float(result_data.get("preferred_skill_score", 0.0)),
                matched_json,
                missing_json,
                result_data.get("recommendation", "Needs Review")
            ))
            conn.commit()
            return cursor.lastrowid

    def get_session_results(self, session_id: int) -> List[Dict[str, Any]]:
        query = """
        SELECT r.*, c.candidate_name, c.email, c.phone, c.location,
               c.resume_filename, c.experience as candidate_exp, c.education as candidate_edu,
               c.extracted_skills as candidate_all_skills,
               j.job_title, j.company_name, j.minimum_experience as required_exp,
               n.screening_status, n.notes
        FROM screening_results r
        JOIN candidates c ON r.candidate_id = c.candidate_id
        JOIN screening_sessions s ON r.session_id = s.session_id
        LEFT JOIN job_descriptions j ON s.job_id = j.job_id
        LEFT JOIN candidate_notes n ON (n.candidate_id = r.candidate_id AND n.session_id = r.session_id)
        WHERE r.session_id = ?
        ORDER BY r.final_score DESC
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (session_id,))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["matched_skills"] = json.loads(item.get("matched_skills") or "[]")
                item["missing_skills"] = json.loads(item.get("missing_skills") or "[]")
                item["candidate_all_skills"] = json.loads(item.get("candidate_all_skills") or "[]")
                results.append(item)
            return results

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        query = """
        SELECT s.*, j.job_title, j.company_name,
               COUNT(r.result_id) as scored_candidates,
               AVG(r.final_score) as avg_score,
               MAX(r.final_score) as max_score
        FROM screening_sessions s
        LEFT JOIN job_descriptions j ON s.job_id = j.job_id
        LEFT JOIN screening_results r ON s.session_id = r.session_id
        GROUP BY s.session_id
        ORDER BY s.screening_date DESC
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return [dict(r) for r in cursor.fetchall()]

    def delete_screening_session(self, session_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM screening_results WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM candidate_notes WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM screening_sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            return True

    # --- Notes and Recruiter Status ---
    def update_candidate_notes(self, candidate_id: int, session_id: int, notes: str, status: str):
        query = """
        INSERT INTO candidate_notes (candidate_id, session_id, notes, screening_status, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(candidate_id, session_id) DO UPDATE SET
            notes = excluded.notes,
            screening_status = excluded.screening_status,
            updated_at = CURRENT_TIMESTAMP
        """
        # Ensure candidate_notes table has unique constraint or handle manually
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT note_id FROM candidate_notes WHERE candidate_id = ? AND session_id = ?",
                (candidate_id, session_id)
            )
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "UPDATE candidate_notes SET notes = ?, screening_status = ?, updated_at = CURRENT_TIMESTAMP WHERE note_id = ?",
                    (notes, status, row["note_id"])
                )
            else:
                cursor.execute(
                    "INSERT INTO candidate_notes (candidate_id, session_id, notes, screening_status) VALUES (?, ?, ?, ?)",
                    (candidate_id, session_id, notes, status)
                )
            conn.commit()

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM candidates")
            total_candidates = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM screening_sessions")
            total_sessions = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*), AVG(final_score) FROM screening_results")
            res = cursor.fetchone()
            total_screened = res[0] or 0
            avg_score = round(res[1] or 0.0, 1)

            cursor.execute("SELECT COUNT(*) FROM screening_results WHERE final_score >= 80")
            shortlisted = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM screening_results WHERE final_score < 45")
            needs_review = cursor.fetchone()[0]

            return {
                "total_candidates": total_candidates,
                "total_sessions": total_sessions,
                "total_screened": total_screened,
                "avg_score": avg_score,
                "shortlisted": shortlisted,
                "needs_review": needs_review
            }

# Global singleton
db = DatabaseManager()

