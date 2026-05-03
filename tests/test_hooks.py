import json
import subprocess
import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".cubicle" / "data" / "telemetry.db"

def run_hook(payload, env=None):
    process = subprocess.Popen(
        ["python3", "src/cubicle/agent_hook.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**subprocess.os.environ, **(env or {})}
    )
    stdout, stderr = process.communicate(input=json.dumps(payload).encode())
    return stdout.decode(), stderr.decode(), process.returncode

def test_minimal():
    print("Starting minimal verification of agent hooks...")
    
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
    
    # 4. Verify DB entries
    print("Verifying database entries...")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Check Gemini
        cursor.execute("SELECT llm_family, event_type FROM telemetry WHERE session_id='gemini_test'")
        row = cursor.fetchone()
        assert row == ("gemini", "pre_tool_use"), f"Gemini DB mismatch: {row}"
        
        # Check Claude
        cursor.execute("SELECT llm_family, event_type FROM telemetry WHERE session_id='claude_test'")
        row = cursor.fetchone()
        assert row == ("claude", "pre_tool_use"), f"Claude DB mismatch: {row}"
        
        # Check Unknown
        cursor.execute("SELECT llm_family, event_type FROM telemetry WHERE session_id='unknown_test'")
        row = cursor.fetchone()
        assert row == ("unknown", "somerandomevent"), f"Unknown DB mismatch: {row}"
        
    print("✅ Minimal verification passed!")

if __name__ == "__main__":
    test_minimal()
