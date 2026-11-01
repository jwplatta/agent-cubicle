# Agent Hooks Implementation Plan

## Objective
Develop a unified, Python-based hook system for Cubicle to capture telemetry data from Gemini, Claude, and Codex agents. The data will be normalized into an action-oriented naming convention (e.g., `pre_tool_use`) and stored in a local SQLite database using a hybrid schema.

## Key Files & Context
- `hooks/cubicle_hook.py` (New): Core Python script to handle incoming hook payloads, normalize data, and write to SQLite.
- `hooks/db.py` (New): SQLite database initialization and interaction logic.
- `bin/cubicle` (Update): The Cubicle CLI tool to include a new command for installing the hooks into user directories.
- Data Storage: `~/.cubicle/data/telemetry.db` (The SQLite database location).

## Implementation Steps

### Phase 1: Database Schema & Initialization
1.  **Create Database Module (`hooks/db.py`)**:
    *   Ensure the directory `~/.cubicle/data/` exists.
    *   Initialize a SQLite database with the following Hybrid Schema:
        *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
        *   `timestamp` (DATETIME DEFAULT CURRENT_TIMESTAMP)
        *   `session_id` (TEXT)
        *   `llm_family` (TEXT - e.g., 'gemini', 'claude', 'codex')
        *   `event_type` (TEXT - normalized action-oriented name)
        *   `model` (TEXT - if available in payload)
        *   `raw_payload` (JSON)

### Phase 2: Event Normalization & Core Hook Script
1.  **Develop the Hook Script (`hooks/cubicle_hook.py`)**:
    *   Configure the script to read JSON from `stdin`.
    *   **Identify Source:** Use environment variables (e.g., `GEMINI_CWD`, `CLAUDE_PROJECT_DIR`) or payload signatures to identify the source LLM family.
    *   **Normalize Event Names:** Map the native event names to the action-oriented convention:
        *   Gemini `BeforeTool` -> `pre_tool_use`
        *   Claude `PreToolUse` -> `pre_tool_use`
        *   Gemini `SessionStart` -> `session_start`, etc.
    *   **Extract Metadata:** Pull out the `session_id`, `model` (if present), and other key context.
    *   **Database Insert:** Write the structured data and the raw JSON payload to the SQLite database.
    *   **Output:** Print the required JSON object to `stdout` so the agent's execution is not blocked, and exit with code `0`.

### Phase 3: CLI Integration (Installation)
1.  **Extend `bin/cubicle`**:
    *   Add support for an `--init-hooks` flag and an `--agent` argument (e.g., `cubicle --init-hooks --agent claude`).
    *   Implement logic to create a wrapper script or symlink the Python hook script into the respective directories:
        *   `~/.gemini/hooks/`
        *   `~/.claude/hooks/`
        *   `~/.codex/hooks/`
    *   Ensure the installed hook files are executable (`chmod +x`).

## Verification & Testing
1.  **Unit Tests**: Validate the normalizer functions in Python accurately map events from Gemini, Claude, and Codex payloads.
2.  **CLI Tests**: Verify `bin/cubicle --init-hooks` correctly creates executable files/symlinks in the right user directories.
3.  **Integration Tests**: Manually trigger hook events simulating Gemini, Claude, and Codex environments to ensure records are successfully inserted into the SQLite DB without blocking `stdout`.
4.  **Schema Check**: Query the SQLite database to confirm the `raw_payload` is valid JSON and key columns are correctly populated.