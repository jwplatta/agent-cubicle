# Cubicle

Cubicle is a unified hook manager and telemetry harness for AI coding agents. It provides a standardized way to capture and normalize usage data from Claude, Gemini, and Codex, storing everything in a central local SQLite database.

## Why I Built This

- **Unified Telemetry:** Capture a global timeline of agent "thinking" and "actions" across different LLM families.
- **Event Normalization:** Maps agent-specific lifecycle events (e.g., `BeforeTool`, `PreToolUse`) to a consistent lowercase standard.
- **Passive Observation:** Non-blocking hook implementation that doesn't interfere with agent performance or results.
- **Independent Installation:** Standalone hook scripts are copied to a central hub, decoupling telemetry from active development of this repo.

## Setup Guide

### 1. Prerequisite
Ensure you have Python 3.9+ installed on your system.

### 2. Local Installation
Install the Cubicle CLI globally (in editable mode for development):

```bash
git clone https://github.com/jwplatta/agent-cubicle.git
cd agent-cubicle
pip install -e .
```

### 3. Initialize Agent Hooks
Point your AI agents to the Cubicle telemetry harness:

```bash
# Setup for Gemini
cubicle init-hooks --agent gemini

# Setup for Claude
cubicle init-hooks --agent claude

# Setup for Codex
cubicle init-hooks --agent codex
```

This command installs stable hook scripts to `~/.cubicle/hooks/` and automatically registers them in your agent's global settings (e.g., `~/.claude/settings.json`).

## Usage & Telemetry

Once initialized, Cubicle captures every tool use, prompt submission, and session event in the background.

### Querying Data
Telemetry is stored in a SQLite database at `~/.cubicle/data/telemetry.db`. You can query it using standard tools:

```bash
sqlite3 ~/.cubicle/data/telemetry.db "SELECT timestamp, llm_family, event_type FROM telemetry ORDER BY id DESC LIMIT 10;"
```

### Removing Hooks
If you need to stop capturing telemetry for a specific agent:

```bash
cubicle del-hooks --agent gemini
```

## Related Tools
Skills are managed separately via the [skillex](https://github.com/jwplatta/skillex) utility. Cubicle focuses exclusively on the telemetry harness and event normalization.

## Notes
- The hooks are designed to be "fail-safe" and will not block the agent if the database is locked or an error occurs.
- The raw JSON payload from every event is preserved in the `raw_payload` column for future analysis.
