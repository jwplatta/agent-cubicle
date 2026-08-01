import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".cubicle" / "data" / "telemetry.db"


def migrate_schema():
    """Remove llm_family column if present. Backs up DB first."""
    if not DB_PATH.exists():
        return
    with sqlite3.connect(DB_PATH) as conn:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(telemetry)").fetchall()]
    if "llm_family" not in cols:
        return

    backup_path = DB_PATH.parent / f"telemetry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DB_PATH, backup_path)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("ALTER TABLE telemetry DROP COLUMN llm_family")
        conn.commit()


def init_db():
    """Initializes the SQLite database and runs any pending migrations."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                event_type TEXT,
                model TEXT,
                raw_payload JSON
            )
        """)
        conn.commit()

    migrate_schema()


def get_model_for_session(session_id):
    """Look up the model from the session_start record for this session_id."""
    if not session_id:
        return None
    if not DB_PATH.exists():
        return None
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT model FROM telemetry WHERE session_id = ? AND event_type = 'session_start' AND model IS NOT NULL LIMIT 1",
            (session_id,)
        ).fetchone()
    return row[0] if row else None


def insert_telemetry(session_id, event_type, model, raw_payload):
    """Inserts a telemetry record into the database."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO telemetry (session_id, event_type, model, raw_payload) VALUES (?, ?, ?, ?)",
            (session_id, event_type, model, json.dumps(raw_payload))
        )
        conn.commit()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
