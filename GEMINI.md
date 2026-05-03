# Gemini Project: Cubicle

## Project Overview

"Cubicle" is a local harness and management tool for AI coding agents. It provides a central place to manage shared logic, configuration, and tools for different agent families (like Claude, Gemini, and Codex), ensuring a consistent and observable developer experience.

The goal is to minimize duplication and maximize the effectiveness of AI agents by centralizing:
- **Shared Skills:** Reusable agent capabilities managed via `skillex`.
- **Shared Configuration:** Centralized management of agent settings and operational boundaries.
- **Unified Telemetry:** A standardized hook system to capture agent behavior across different models.
- **Interoperability:** A common framework for agents to interact with local projects and shared resources.

## Key Current Feature: Unified Hooks

Cubicle currently provides a standardized way to capture telemetry data from agents like Claude, Gemini, and Codex, normalizing their native events into a consistent format and storing them in a local SQLite database at `~/.cubicle/data/telemetry.db`.

## Installation

```bash
# Install the cubicle CLI globally (in editable mode for development)
pip install -e .

# Initialize telemetry hooks for a specific agent
cubicle init-hooks --agent gemini
```

## CLI Usage

- `cubicle init-hooks --agent <name>`: Installs telemetry hooks and registers them in agent settings.
- `cubicle del-hooks --agent <name>`: Removes cubicle hooks and unregisters them.

## Telemetry Database Schema

Stored in `~/.cubicle/data/telemetry.db`:
- **`timestamp`**: UTC time of the event.
- **`llm_family`**: gemini, claude, codex, etc.
- **`event_type`**: Normalized event name (e.g., `pre_tool_use`, `session_start`).
- **`raw_payload`**: The complete JSON object provided by the agent.

## Future Vision

Cubicle will expand to become the primary local entry point for complex agent workflows, including:
- Automated pull request management.
- Task orchestration via Todoist or local backlogs.
- Shared memory and context across different agent sessions.
