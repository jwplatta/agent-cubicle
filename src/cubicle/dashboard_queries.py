import json
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path.home() / ".cubicle" / "data" / "telemetry.db"

# Normalized event type sets (handles both pre_tool_use and pretooluse variants)
_TOOL_USE_EVENTS = "('pre_tool_use','pretooluse')"
_POST_TOOL_EVENTS = "('post_tool_use','posttooluse')"
_PROMPT_EVENTS = "('user_prompt_submit','userpromptsubmit')"
_SESSION_START_EVENTS = "('session_start','sessionstart')"
_SESSION_END_EVENTS = "('session_end','sessionend','agent_stop')"
_PERMISSION_EVENTS = "('permission_request','permissionrequest')"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def infer_agent(model) -> str:
    if not model or not isinstance(model, str):
        return "Unknown"
    m = model.lower()
    if m.startswith("claude"):
        return "Claude"
    if m.startswith("gpt") or "codex" in m:
        return "Codex"
    if "gemini" in m:
        return "Antigravity"
    if "copilot" in m:
        return "Copilot"
    return "Unknown"


def get_summary_stats() -> dict:
    with _connect() as conn:
        sessions_row = conn.execute(
            "SELECT COUNT(DISTINCT session_id) as n FROM telemetry"
        ).fetchone()
        tool_calls_row = conn.execute(
            "SELECT COUNT(*) as n FROM telemetry WHERE LOWER(REPLACE(event_type,'_','')) = 'pretooluse'"
        ).fetchone()
        prompts_row = conn.execute(
            "SELECT COUNT(*) as n FROM telemetry WHERE LOWER(REPLACE(event_type,'_','')) = 'userpromptsubmit'"
        ).fetchone()
        duration_row = conn.execute("""
            SELECT AVG((julianday(last_ts) - julianday(first_ts)) * 24 * 60) as avg_min
            FROM (
                SELECT session_id,
                       MIN(timestamp) as first_ts,
                       MAX(timestamp) as last_ts
                FROM telemetry
                GROUP BY session_id
                HAVING COUNT(*) > 1
            )
        """).fetchone()
        top_model_row = conn.execute("""
            SELECT model, COUNT(DISTINCT session_id) as n
            FROM telemetry
            WHERE model IS NOT NULL AND model != ''
            GROUP BY model
            ORDER BY n DESC
            LIMIT 1
        """).fetchone()

    return {
        "total_sessions": sessions_row["n"],
        "total_tool_calls": tool_calls_row["n"],
        "total_prompts": prompts_row["n"],
        "avg_duration_min": round(duration_row["avg_min"] or 0, 1),
        "top_model": top_model_row["model"] if top_model_row else "N/A",
    }


def get_sessions() -> pd.DataFrame:
    with _connect() as conn:
        df = pd.read_sql_query("""
            SELECT
                t.session_id,
                t.model,
                MIN(t.timestamp) as start_time,
                MAX(t.timestamp) as end_time,
                ROUND((julianday(MAX(t.timestamp)) - julianday(MIN(t.timestamp))) * 24 * 60, 1) as duration_min,
                COUNT(*) as event_count,
                SUM(CASE WHEN LOWER(REPLACE(t.event_type,'_','')) = 'userpromptsubmit' THEN 1 ELSE 0 END) as prompt_count,
                SUM(CASE WHEN LOWER(REPLACE(t.event_type,'_','')) = 'pretooluse' THEN 1 ELSE 0 END) as tool_count,
                SUM(CASE WHEN LOWER(REPLACE(t.event_type,'_','')) = 'permissionrequest' THEN 1 ELSE 0 END) as permission_count,
                MAX(CASE WHEN t.raw_payload LIKE '%cwd%' THEN json_extract(t.raw_payload, '$.cwd') END) as cwd
            FROM telemetry t
            GROUP BY t.session_id
            ORDER BY start_time DESC
        """, conn)

    df["agent"] = df["model"].apply(infer_agent)
    df["repo"] = df["cwd"].apply(lambda x: Path(x).name if isinstance(x, str) and x else "unknown")
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])
    df["session_short"] = df["session_id"].str[:8]
    return df


def get_daily_sessions(days: int = 30) -> pd.DataFrame:
    with _connect() as conn:
        df = pd.read_sql_query(f"""
            SELECT
                DATE(first_ts) as date,
                model,
                COUNT(*) as sessions
            FROM (
                SELECT session_id, model, MIN(timestamp) as first_ts
                FROM telemetry
                GROUP BY session_id
            )
            WHERE first_ts >= DATE('now', '-{days} days')
            GROUP BY DATE(first_ts), model
            ORDER BY date
        """, conn)

    df["agent"] = df["model"].apply(infer_agent)
    df["date"] = pd.to_datetime(df["date"])
    return df


def get_model_distribution() -> pd.DataFrame:
    with _connect() as conn:
        df = pd.read_sql_query("""
            SELECT
                model,
                COUNT(DISTINCT session_id) as sessions,
                SUM(CASE WHEN LOWER(REPLACE(event_type,'_','')) = 'pretooluse' THEN 1 ELSE 0 END) as tool_calls
            FROM telemetry
            WHERE model IS NOT NULL AND model != ''
            GROUP BY model
            ORDER BY sessions DESC
        """, conn)
    df["agent"] = df["model"].apply(infer_agent)
    return df


def get_repo_distribution() -> pd.DataFrame:
    with _connect() as conn:
        df = pd.read_sql_query("""
            SELECT
                json_extract(raw_payload, '$.cwd') as cwd,
                COUNT(DISTINCT session_id) as sessions,
                SUM(CASE WHEN LOWER(REPLACE(event_type,'_','')) = 'pretooluse' THEN 1 ELSE 0 END) as tool_calls
            FROM telemetry
            WHERE raw_payload LIKE '%cwd%'
            GROUP BY cwd
            ORDER BY tool_calls DESC
            LIMIT 20
        """, conn)
    df["repo"] = df["cwd"].apply(lambda x: Path(x).name if isinstance(x, str) and x else "unknown")
    df = df.groupby("repo", as_index=False).agg({"sessions": "sum", "tool_calls": "sum"})
    df = df.sort_values("tool_calls", ascending=False).head(15)
    return df


def get_tool_usage() -> pd.DataFrame:
    with _connect() as conn:
        df = pd.read_sql_query("""
            SELECT
                json_extract(raw_payload, '$.tool_name') as tool_name,
                COUNT(*) as count,
                COUNT(DISTINCT session_id) as sessions
            FROM telemetry
            WHERE LOWER(REPLACE(event_type,'_','')) = 'pretooluse'
              AND json_extract(raw_payload, '$.tool_name') IS NOT NULL
            GROUP BY tool_name
            ORDER BY count DESC
            LIMIT 20
        """, conn)
    return df


def get_session_events(session_id: str) -> pd.DataFrame:
    with _connect() as conn:
        rows = conn.execute("""
            SELECT timestamp, event_type, raw_payload
            FROM telemetry
            WHERE session_id = ?
            ORDER BY timestamp ASC, id ASC
        """, (session_id,)).fetchall()

    records = []
    for row in rows:
        try:
            payload = json.loads(row["raw_payload"])
        except Exception:
            payload = {}

        norm = row["event_type"].lower().replace("_", "")
        tool_name = payload.get("tool_name")

        prompt_text = None
        if norm == "userpromptsubmit":
            prompt_text = payload.get("prompt") or payload.get("message")

        tool_response = None
        if norm == "posttooluse":
            resp = payload.get("tool_response")
            if isinstance(resp, dict):
                tool_response = resp.get("stdout") or resp.get("output") or json.dumps(resp)
            elif isinstance(resp, str):
                tool_response = resp
            if tool_response and len(tool_response) > 400:
                tool_response = tool_response[:400] + "…"

        tool_input = None
        if norm == "pretooluse":
            ti = payload.get("tool_input")
            if ti:
                tool_input = json.dumps(ti) if not isinstance(ti, str) else ti
                if len(tool_input) > 400:
                    tool_input = tool_input[:400] + "…"

        notification_msg = None
        if norm in ("notification", "permissionrequest"):
            notification_msg = payload.get("message") or payload.get("reason")

        assistant_message = None
        if norm in ("turncomplete", "stop"):
            assistant_message = payload.get("last_assistant_message")

        records.append({
            "timestamp": row["timestamp"],
            "event_type": row["event_type"],
            "norm_event": norm,
            "tool_name": tool_name,
            "prompt_text": prompt_text,
            "tool_input": tool_input,
            "tool_response": tool_response,
            "notification_msg": notification_msg,
            "assistant_message": assistant_message,
            "cwd": payload.get("cwd"),
        })

    return pd.DataFrame(records)


def get_usage_heatmap() -> pd.DataFrame:
    """Returns session counts by day-of-week and hour-of-day."""
    with _connect() as conn:
        df = pd.read_sql_query("""
            SELECT
                CAST(strftime('%w', first_ts) AS INTEGER) as dow,
                CAST(strftime('%H', first_ts) AS INTEGER) as hour,
                COUNT(*) as sessions
            FROM (
                SELECT session_id, MIN(timestamp) as first_ts
                FROM telemetry
                GROUP BY session_id
            )
            GROUP BY dow, hour
        """, conn)
    return df


def get_error_stats() -> pd.DataFrame:
    with _connect() as conn:
        df = pd.read_sql_query("""
            SELECT
                model,
                SUM(CASE WHEN LOWER(REPLACE(event_type,'_','')) = 'permissionrequest' THEN 1 ELSE 0 END) as permission_requests,
                SUM(CASE WHEN LOWER(REPLACE(event_type,'_','')) = 'notification'
                         AND raw_payload LIKE '%permission_prompt%' THEN 1 ELSE 0 END) as permission_prompts
            FROM telemetry
            WHERE model IS NOT NULL AND model != ''
            GROUP BY model
            ORDER BY permission_requests DESC
        """, conn)
    df["agent"] = df["model"].apply(infer_agent)
    return df
