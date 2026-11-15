import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "mailgenius.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature TEXT NOT NULL,
            title TEXT,
            input_text TEXT,
            output_text TEXT,
            metadata TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )""")
        conn.commit()

def save_activity(feature, title, input_text="", output_text="", metadata=""):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO activity(feature,title,input_text,output_text,metadata,created_at) VALUES(?,?,?,?,?,?)",
            (feature, title, input_text, output_text, metadata, datetime.now().isoformat(timespec="seconds"))
        )
        conn.commit()

def get_stats():
    with get_connection() as conn:
        rows = conn.execute("SELECT feature, COUNT(*) AS n FROM activity GROUP BY feature").fetchall()
    counts = {r["feature"]: r["n"] for r in rows}
    generated = counts.get("Email Generator", 0) + counts.get("Smart Reply", 0) + counts.get("Follow-up", 0)
    analysed = sum(counts.get(k, 0) for k in ["Phishing Analysis", "Sentiment Analysis", "Quality Analysis"])
    phishing = counts.get("Phishing Analysis", 0)
    return {"generated": generated, "analysed": analysed, "phishing": phishing, "tasks": sum(counts.values()), "by_feature": counts}

def get_recent(limit=8, feature=None):
    with get_connection() as conn:
        if feature and feature != "All":
            return conn.execute("SELECT * FROM activity WHERE feature=? ORDER BY id DESC LIMIT ?", (feature, limit)).fetchall()
        return conn.execute("SELECT * FROM activity ORDER BY id DESC LIMIT ?", (limit,)).fetchall()

def search_history(term="", feature="All"):
    sql = "SELECT * FROM activity WHERE (title LIKE ? OR input_text LIKE ? OR output_text LIKE ?)"
    args = [f"%{term}%"] * 3
    if feature != "All":
        sql += " AND feature=?"
        args.append(feature)
    sql += " ORDER BY id DESC"
    with get_connection() as conn:
        return conn.execute(sql, args).fetchall()

def delete_activity(record_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM activity WHERE id=?", (record_id,))
        conn.commit()

def clear_history():
    with get_connection() as conn:
        conn.execute("DELETE FROM activity")
        conn.commit()
