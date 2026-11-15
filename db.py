import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "mailgen.db"

def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Create and return a thread-safe connection to the SQLite database."""
    target_path = db_path or DB_PATH
    conn = sqlite3.connect(str(target_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Optional[Path] = None) -> None:
    """Initialize the SQLite database schema if not already present."""
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_name TEXT NOT NULL,
                recipient_email TEXT DEFAULT '',
                email_subject TEXT NOT NULL,
                email_body TEXT NOT NULL,
                email_category TEXT NOT NULL,
                writing_tone TEXT NOT NULL,
                email_length TEXT DEFAULT 'Medium',
                action_type TEXT DEFAULT 'Generated',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_emails_created ON emails(created_at DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_emails_category ON emails(email_category)")
        conn.commit()

def save_email(
    recipient_name: str,
    email_subject: str,
    email_body: str,
    email_category: str,
    writing_tone: str,
    recipient_email: str = "",
    email_length: str = "Medium",
    action_type: str = "Generated",
    db_path: Optional[Path] = None
) -> int:
    """
    Insert a generated or processed email record into SQLite.
    Returns the newly created email ID.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO emails (
                recipient_name, recipient_email, email_subject, email_body,
                email_category, writing_tone, email_length, action_type, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                recipient_name.strip() or "Valued Recipient",
                recipient_email.strip(),
                email_subject.strip() or "Untitled Email",
                email_body.strip(),
                email_category.strip() or "Professional Email",
                writing_tone.strip() or "Professional",
                email_length.strip() or "Medium",
                action_type.strip() or "Generated",
                now_str
            )
        )
        conn.commit()
        return cursor.lastrowid

def get_all_emails(
    category: Optional[str] = None,
    tone: Optional[str] = None,
    search_term: Optional[str] = None,
    limit: Optional[int] = None,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieve filtered email records ordered by creation date descending."""
    query = "SELECT * FROM emails WHERE 1=1"
    params: List[Any] = []

    if category and category != "All Categories":
        query += " AND email_category = ?"
        params.append(category)

    if tone and tone != "All Tones":
        query += " AND writing_tone = ?"
        params.append(tone)

    if search_term and search_term.strip():
        term = f"%{search_term.strip()}%"
        query += " AND (email_subject LIKE ? OR email_body LIKE ? OR recipient_name LIKE ? OR recipient_email LIKE ?)"
        params.extend([term, term, term, term])

    query += " ORDER BY id DESC"

    if limit and limit > 0:
        query += " LIMIT ?"
        params.append(limit)

    with get_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

def get_email_by_id(email_id: int, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Fetch a single email record by primary key ID."""
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM emails WHERE id = ?", (email_id,)).fetchone()
        return dict(row) if row else None

def delete_email(email_id: int, db_path: Optional[Path] = None) -> bool:
    """Delete a specific email record by ID."""
    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM emails WHERE id = ?", (email_id,))
        conn.commit()
        return cursor.rowcount > 0

def clear_all_emails(db_path: Optional[Path] = None) -> bool:
    """Clear all records from the emails table."""
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM emails")
        conn.commit()
        return True

def get_statistics(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Calculate aggregated metrics for dashboard display."""
    today_prefix = datetime.now().strftime("%Y-%m-%d")
    with get_connection(db_path) as conn:
        total = conn.execute("SELECT COUNT(*) AS total FROM emails").fetchone()["total"]
        today_count = conn.execute(
            "SELECT COUNT(*) AS count_today FROM emails WHERE created_at LIKE ?",
            (f"{today_prefix}%",)
        ).fetchone()["count_today"]

        category_rows = conn.execute(
            "SELECT email_category, COUNT(*) as cnt FROM emails GROUP BY email_category ORDER BY cnt DESC"
        ).fetchall()
        categories = {r["email_category"]: r["cnt"] for r in category_rows}

        tone_rows = conn.execute(
            "SELECT writing_tone, COUNT(*) as cnt FROM emails GROUP BY writing_tone ORDER BY cnt DESC"
        ).fetchall()
        tones = {r["writing_tone"]: r["cnt"] for r in tone_rows}

        action_rows = conn.execute(
            "SELECT action_type, COUNT(*) as cnt FROM emails GROUP BY action_type"
        ).fetchall()
        actions = {r["action_type"]: r["cnt"] for r in action_rows}

        recent_rows = conn.execute(
            "SELECT * FROM emails ORDER BY id DESC LIMIT 5"
        ).fetchall()
        recent = [dict(r) for r in recent_rows]

    return {
        "total_emails": total,
        "today_emails": today_count,
        "categories": categories,
        "tones": tones,
        "actions": actions,
        "generated_count": actions.get("Generated", 0),
        "rewritten_count": actions.get("Rewritten", 0),
        "reply_count": actions.get("Reply", 0),
        "recent_emails": recent
    }
