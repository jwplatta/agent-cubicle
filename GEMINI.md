# Gemini Project: Cubicle

## Project Overview

"Cubicle" is a unified hook manager for AI coding agents. It provides a standardized way to capture telemetry data from agents like Claude, Gemini, and Codex, normalizing their native events into a consistent format and storing them in a local SQLite database.

The goal is to provide a single harness for capturing agent usage patterns without requiring complex per-agent setup.

## Key Features

- **Unified Hooks:** Standardized Python scripts that capture input/output and tool usage across different LLM families.
- **Telemetry Database:** A central SQLite database at `~/.cubicle/data/telemetry.db` for easy querying of agent activity.
- **Clean Installation:** A CLI tool that installs standalone hook scripts into agent-specific home directories, ensuring they remain independent of the core repository's state.

## Installation

```bash
# Install the cubicle CLI globally (in editable mode for development)
pip install -e .

# Initialize hooks for a specific agent
cubicle init-hooks --agent gemini
```

## Commands

- `cubicle init-hooks --agent <name>`: Installs telemetry hooks for the specified agent (claude, gemini, codex, or copilot).
- `cubicle clean --agent <name>`: Removes cubicle hooks from the specified agent.

## Telemetry Data

Telemetry is stored in a hybrid schema:
- **`timestamp`**: When the event occurred.
- **`llm_family`**: gemini, claude, codex, etc.
- **`event_type`**: Normalized event name (e.g., `pre_tool_use`, `session_start`).
- **`raw_payload`**: The complete JSON object provided by the agent.

Query the data:
```bash
sqlite3 ~/.cubicle/data/telemetry.db "SELECT * FROM telemetry;"
```
