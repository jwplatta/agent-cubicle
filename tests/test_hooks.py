import json
import sqlite3
import subprocess
from pathlib import Path

import yaml

SRC_DIR = Path(__file__).resolve().parents[1] / "src" / "cubicle"
CLAUDE_HOOK_PATH = SRC_DIR / "claude_hook.py"
CODEX_HOOK_PATH = SRC_DIR / "codex_hook.py"
GEMINI_HOOK_PATH = SRC_DIR / "gemini_hook.py"


def write_config(home_dir):
    config_dir = home_dir / ".cubicle"
    config_dir.mkdir(parents=True, exist_ok=True)
    source_config = SRC_DIR / "default_config.yaml"
    with open(source_config) as f:
        config = yaml.safe_load(f)
    with open(config_dir / "config.yaml", "w") as f:
        yaml.safe_dump(config, f)


def db_path_for_home(home_dir):
    return home_dir / ".cubicle" / "data" / "telemetry.db"


def run_hook(hook_path, payload, home_dir, env=None):
    base_env = {k: v for k, v in subprocess.os.environ.items()}
    base_env["HOME"] = str(home_dir)
    process = subprocess.Popen(
        ["python3", str(hook_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**base_env, **(env or {})}
    )
    stdout, stderr = process.communicate(input=json.dumps(payload).encode())
    return stdout.decode(), stderr.decode(), process.returncode


def init_test_db(db_path, session_ids):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
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
        conn.executemany(
            "DELETE FROM telemetry WHERE session_id = ?",
            [(s,) for s in session_ids]
        )
        conn.commit()


def test_gemini_hook():
    print("Testing Gemini hook...")
    home_dir = Path(__file__).resolve().parents[1] / "tmp" / "test_gemini_home"
    write_config(home_dir)
    db_path = db_path_for_home(home_dir)
    init_test_db(db_path, ["gemini_test"])

    stdout, stderr, code = run_hook(
        GEMINI_HOOK_PATH,
        {"hook_event_name": "BeforeTool", "session_id": "gemini_test", "model": "gemini-pro"},
        home_dir,
    )
    assert code == 0, f"Gemini hook failed: {stderr}"
    assert stdout.strip() == "{}", f"Unexpected stdout: {stdout}"

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT event_type, model FROM telemetry WHERE session_id='gemini_test' ORDER BY id DESC LIMIT 1"
        ).fetchone()
    assert row == ("pre_tool_use", "gemini-pro"), f"Gemini DB mismatch: {row}"
    print("  ✅ Gemini hook passed")


def test_codex_hook():
    print("Testing Codex hook...")
    home_dir = Path(__file__).resolve().parents[1] / "tmp" / "test_codex_home"
    write_config(home_dir)
    db_path = db_path_for_home(home_dir)
    init_test_db(db_path, ["codex_test"])

    stdout, stderr, code = run_hook(
        CODEX_HOOK_PATH,
        {"hook_event_name": "PostToolUse", "session_id": "codex_test", "model": "gpt-5.4", "cwd": "/tmp"},
        home_dir,
    )
    assert code == 0, f"Codex hook failed: {stderr}"

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT event_type, model FROM telemetry WHERE session_id='codex_test' ORDER BY id DESC LIMIT 1"
        ).fetchone()
    assert row == ("post_tool_use", "gpt-5.4"), f"Codex DB mismatch: {row}"
    print("  ✅ Codex hook passed")


def test_claude_hook_session_start_model():
    print("Testing Claude hook — model present on session_start...")
    home_dir = Path(__file__).resolve().parents[1] / "tmp" / "test_claude_home"
    write_config(home_dir)
    db_path = db_path_for_home(home_dir)
    init_test_db(db_path, ["claude_session_test"])

    # session_start carries the model
    stdout, stderr, code = run_hook(
        CLAUDE_HOOK_PATH,
        {"hook_event_name": "SessionStart", "session_id": "claude_session_test", "model": "claude-sonnet-4-6"},
        home_dir,
    )
    assert code == 0, f"Claude session_start hook failed: {stderr}"

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT event_type, model FROM telemetry WHERE session_id='claude_session_test' ORDER BY id DESC LIMIT 1"
        ).fetchone()
    assert row == ("session_start", "claude-sonnet-4-6"), f"Claude session_start DB mismatch: {row}"
    print("  ✅ Claude session_start model captured")


def test_claude_hook_model_resolution_from_db():
    print("Testing Claude hook — model resolved from session_start record for tool events...")
    home_dir = Path(__file__).resolve().parents[1] / "tmp" / "test_claude_home"
    write_config(home_dir)
    db_path = db_path_for_home(home_dir)
    init_test_db(db_path, ["claude_resolution_test"])

    # First: session_start populates the model in DB
    run_hook(
        CLAUDE_HOOK_PATH,
        {"hook_event_name": "SessionStart", "session_id": "claude_resolution_test", "model": "claude-sonnet-4-6"},
        home_dir,
    )

    # Then: PreToolUse has no model field — should be resolved via DB lookup
    stdout, stderr, code = run_hook(
        CLAUDE_HOOK_PATH,
        {
            "hook_event_name": "PreToolUse",
            "session_id": "claude_resolution_test",
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/foo.py"},
            "tool_use_id": "toolu_abc123",
        },
        home_dir,
    )
    assert code == 0, f"Claude PreToolUse hook failed: {stderr}"

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT event_type, model FROM telemetry WHERE session_id='claude_resolution_test' AND event_type='pre_tool_use' ORDER BY id DESC LIMIT 1"
        ).fetchone()
    assert row is not None, "No pre_tool_use record found"
    assert row[1] == "claude-sonnet-4-6", f"Model not resolved from session: {row}"
    print("  ✅ Claude model correctly resolved from session_start record")


def test_minimal():
    """Run all hook tests."""
    print("Starting per-agent hook verification...")
    test_gemini_hook()
    test_codex_hook()
    test_claude_hook_session_start_model()
    test_claude_hook_model_resolution_from_db()
    print("✅ All hook tests passed!")


if __name__ == "__main__":
    test_minimal()
