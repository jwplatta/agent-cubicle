import json
import subprocess
import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".cubicle" / "data" / "telemetry.db"
HOOK_PATH = Path(__file__).resolve().parents[1] / "src" / "cubicle" / "agent_hook.py"
AGENT_ENV_PREFIXES = ("CODEX_", "CLAUDE_", "GEMINI_", "COPILOT_")

def run_hook(payload, env=None):
    base_env = {
        key: value
        for key, value in subprocess.os.environ.items()
        if not key.startswith(AGENT_ENV_PREFIXES)
    }
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
    test_session_ids = [
        "gemini_test",
        "claude_test",
        "unknown_test",
        "codex_env_test",
        "codex_payload_test",
    ]
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            "DELETE FROM telemetry WHERE session_id = ?",
            [(session_id,) for session_id in test_session_ids]
        )
        conn.commit()
    
    # 1. Test Gemini normalization
    print("Testing Gemini normalization...")
    stdout, stderr, code = run_hook(
        {"hook_event_name": "BeforeTool", "session_id": "gemini_test", "model": "gemini-pro"},
        {"GEMINI_CWD": "/tmp"}
    )
    assert code == 0, f"Gemini hook failed: {stderr}"
    assert stdout.strip() == "{}", f"Unexpected stdout: {stdout}"
    
    # 2. Test Claude normalization
    print("Testing Claude normalization...")
    stdout, stderr, code = run_hook(
        {"event": "PreToolUse", "session_id": "claude_test", "model": "claude-3"},
        {"CLAUDE_PROJECT_DIR": "/tmp"}
    )
    assert code == 0, f"Claude hook failed: {stderr}"
    
    # 3. Test Unknown fallback
    print("Testing Unknown fallback...")
    stdout, stderr, code = run_hook(
        {"event": "SomeRandomEvent", "session_id": "unknown_test"}
    )
    assert code == 0, f"Unknown hook failed: {stderr}"

    # 4. Test Codex normalization via actual env var shape
    print("Testing Codex normalization from env...")
    stdout, stderr, code = run_hook(
        {"hook_event_name": "PostToolUse", "session_id": "codex_env_test", "model": "gpt-5.4", "cwd": "/tmp"},
        {"CODEX_THREAD_ID": "thread_123"}
    )
    assert code == 0, f"Codex env hook failed: {stderr}"

    # 5. Test Codex normalization via transcript path fallback
    print("Testing Codex normalization from payload...")
    stdout, stderr, code = run_hook(
        {
            "hook_event_name": "UserPromptSubmit",
            "session_id": "codex_payload_test",
            "model": "gpt-5.4",
            "cwd": "/tmp",
            "transcript_path": "/Users/test/.codex/sessions/2026/05/03/session.jsonl"
        }
    )
    assert code == 0, f"Codex payload hook failed: {stderr}"
    
    # 6. Verify DB entries
    print("Verifying database entries...")
    with sqlite3.connect(DB_PATH) as conn:
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

        # Check Codex from payload fallback
        cursor.execute("SELECT llm_family, event_type FROM telemetry WHERE session_id='codex_payload_test' ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        assert row == ("codex", "user_prompt_submit"), f"Codex payload DB mismatch: {row}"
        
    print("✅ Minimal verification passed!")

if __name__ == "__main__":
    test_minimal()
