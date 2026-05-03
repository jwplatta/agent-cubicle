import sqlite3
import os
import json
from pathlib import Path

DB_PATH = Path.home() / ".cubicle" / "data" / "telemetry.db"

def init_db():
    """Initializes the SQLite database with the hybrid schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                llm_family TEXT,
                event_type TEXT,
                model TEXT,
                raw_payload JSON
            )
        """)
        conn.commit()

def insert_telemetry(session_id, llm_family, event_type, model, raw_payload):
    """Inserts a telemetry record into the database."""
    init_db() # Ensure DB is initialized
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO telemetry (session_id, llm_family, event_type, model, raw_payload) VALUES (?, ?, ?, ?, ?)",
            (session_id, llm_family, event_type, model, json.dumps(raw_payload))
        )
        conn.commit()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
