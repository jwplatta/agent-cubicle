# Cubicle

Cubicle is a local harness and management tool for AI coding agents. It provides a central place to manage shared logic, configuration, and tools for different agent families (like Claude, Gemini, and Codex), ensuring a consistent and observable developer experience.

The goal of Cubicle is to eliminate duplication across different agent setups and provide a single interface for extending agent capabilities.

## Current Features

### 1. Unified Telemetry Harness
A standardized way to capture and normalize usage data across different LLM families, storing everything in a central local SQLite database.

- **Event Normalization:** Maps agent-specific lifecycle events (e.g., `BeforeTool`, `PreToolUse`) to a consistent standard.
- **Centralized Storage:** A SQLite database at `~/.cubicle/data/telemetry.db` for easy querying of agent activity.
- **Passive Observation:** Non-blocking hook implementation that doesn't interfere with agent performance.

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

### Commands

- `cubicle setup`: Initializes the Cubicle home directory and stable resources. Use `--force` to refresh code from the repository.
- `cubicle init-hooks --agent <name>`: Installs telemetry hooks and registers them in agent settings.
- `cubicle del-hooks --agent <name>`: Unregisters hooks from the specified agent.
- `cubicle help`: Shows this help message.

## Telemetry Usage

Once initialized, Cubicle captures tool use, prompt submission, and session events in the background.

### Querying Data
Query the SQLite database at `~/.cubicle/data/telemetry.db`:

```bash
sqlite3 ~/.cubicle/data/telemetry.db "SELECT timestamp, llm_family, event_type FROM telemetry ORDER BY id DESC LIMIT 10;"
```

## Related Tools
- **[skillex](https://github.com/jwplatta/skillex):** Manages versioned agent skills. Cubicle and Skillex work together to provide a robust shared environment for coding agents.

## Notes
- The hooks are designed to be "fail-safe" and will not block the agent if an error occurs.
- The raw JSON payload from every event is preserved in the `raw_payload` column for future analysis.
