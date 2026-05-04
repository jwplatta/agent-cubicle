import json
import subprocess
import sqlite3
from pathlib import Path

import yaml

HOOK_PATH = Path(__file__).resolve().parents[1] / "src" / "cubicle" / "agent_hook.py"
AGENT_ENV_PREFIXES = ("CODEX_", "CLAUDE_", "GEMINI_", "COPILOT_")

def write_config(home_dir):
    config_dir = home_dir / ".cubicle"
    config_dir.mkdir(parents=True, exist_ok=True)
    source_config = Path(__file__).resolve().parents[1] / "src" / "cubicle" / "default_config.yaml"
    with open(source_config) as f:
        config = yaml.safe_load(f)
    with open(config_dir / "config.yaml", "w") as f:
        yaml.safe_dump(config, f)


def db_path_for_home(home_dir):
    return home_dir / ".cubicle" / "data" / "telemetry.db"


def run_hook(payload, home_dir, env=None):
    base_env = {
        key: value
        for key, value in subprocess.os.environ.items()
        if not key.startswith(AGENT_ENV_PREFIXES)
    }
    base_env["HOME"] = str(home_dir)
    process = subprocess.Popen(
        ["python3", str(HOOK_PATH)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**base_env, **(env or {})}
    )
    stdout, stderr = process.communicate(input=json.dumps(payload).encode())
    return stdout.decode(), stderr.decode(), process.returncode

def test_minimal():
    print("Starting minimal verification of agent hooks...")
    home_dir = Path(__file__).resolve().parents[1] / "tmp" / "test_hook_home"
    write_config(home_dir)
    db_path = db_path_for_home(home_dir)
    test_session_ids = [
        "gemini_test",
        "claude_test",
        "unknown_test",
        "codex_env_test",
        "heuristic_only_test",
    ]
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                llm_family TEXT,
                event_type TEXT,
                model TEXT,
                raw_payload JSON
            )
            """
        )
        conn.executemany(
            "DELETE FROM telemetry WHERE session_id = ?",
            [(session_id,) for session_id in test_session_ids]
        )
        conn.commit()
    
    # 1. Test Gemini normalization
    print("Testing Gemini normalization...")
    stdout, stderr, code = run_hook(
        {"hook_event_name": "BeforeTool", "session_id": "gemini_test", "model": "gemini-pro"},
        home_dir,
        {"CUBICLE_LLM_FAMILY": "gemini"}
    )
    assert code == 0, f"Gemini hook failed: {stderr}"
    assert stdout.strip() == "{}", f"Unexpected stdout: {stdout}"
    
    # 2. Test Claude normalization
    print("Testing Claude normalization...")
    stdout, stderr, code = run_hook(
        {"event": "PreToolUse", "session_id": "claude_test", "model": "claude-3"},
        home_dir,
        {"CUBICLE_LLM_FAMILY": "claude"}
    )
    assert code == 0, f"Claude hook failed: {stderr}"
    
    # 3. Test Unknown fallback
    print("Testing Unknown fallback...")
    stdout, stderr, code = run_hook(
        {"event": "SomeRandomEvent", "session_id": "unknown_test"},
        home_dir
    )
    assert code == 0, f"Unknown hook failed: {stderr}"

    # 4. Test Codex normalization via Cubicle env var
    print("Testing Codex normalization from env...")
    stdout, stderr, code = run_hook(
        {"hook_event_name": "PostToolUse", "session_id": "codex_env_test", "model": "gpt-5.4", "cwd": "/tmp"},
        home_dir,
        {"CUBICLE_LLM_FAMILY": "codex"}
    )
    assert code == 0, f"Codex env hook failed: {stderr}"

    # 5. Old heuristic-only signals should no longer classify the agent family
    print("Testing that heuristic-only payloads remain unknown...")
    stdout, stderr, code = run_hook(
        {
            "hook_event_name": "UserPromptSubmit",
            "session_id": "heuristic_only_test",
            "model": "gpt-5.4",
            "cwd": "/tmp",
            "transcript_path": "/Users/test/.codex/sessions/2026/05/03/session.jsonl"
        },
        home_dir,
        {"CODEX_THREAD_ID": "thread_123"}
    )
    assert code == 0, f"Heuristic-only hook failed: {stderr}"
    
    # 6. Verify DB entries
    print("Verifying database entries...")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Check Gemini
        cursor.execute("SELECT llm_family, event_type FROM telemetry WHERE session_id='gemini_test' ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        assert row == ("gemini", "pre_tool_use"), f"Gemini DB mismatch: {row}"
        
        # Check Claude
        cursor.execute("SELECT llm_family, event_type FROM telemetry WHERE session_id='claude_test' ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        assert row == ("claude", "pre_tool_use"), f"Claude DB mismatch: {row}"
        
        # Check Unknown
        cursor.execute("SELECT llm_family, event_type FROM telemetry WHERE session_id='unknown_test' ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        assert row == ("unknown", "somerandomevent"), f"Unknown DB mismatch: {row}"

        # Check Codex from env
        cursor.execute("SELECT llm_family, event_type FROM telemetry WHERE session_id='codex_env_test' ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        assert row == ("codex", "post_tool_use"), f"Codex env DB mismatch: {row}"

        # Check heuristic-only fallback
        cursor.execute("SELECT llm_family, event_type FROM telemetry WHERE session_id='heuristic_only_test' ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        assert row == ("unknown", "userpromptsubmit"), f"Heuristic-only DB mismatch: {row}"

    print("✅ Minimal verification passed!")

if __name__ == "__main__":
    test_minimal()
