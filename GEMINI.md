# Gemini Project: Cubicle

## Project Overview

Cubicle is a local harness for coding agents. It keeps shared configuration, skills, commands, prompts, and notes in one repo, then uses the `./cubicle` CLI to link the right files into each agent's home directory before launching that agent inside a chosen local project.

The goal is to minimize duplication and keep agent setup easy to inspect and change:
- **Unified configuration:** agent-specific files in `configs/`
- **Shared commands:** common operational behavior across agents in `commands/`
- **Interoperability:** one repo-driven workflow for Claude, Codex, Copilot, and Gemini

Skills are managed separately via the `skillex` utility.

## Running Cubicle

### Prerequisites

- A local install of the agent CLI you want to run
- An `.env` file with the needed keys and `PROJECTS_DIR`

### Key Commands

```bash
./cubicle help
./cubicle run --agent gemini --project cubicle
./cubicle clean --agent gemini
```

`run` installs or refreshes symlinks, validates the project path under `PROJECTS_DIR`, changes into that project directory, and launches the selected agent directly on the host.

## Development Conventions

### Agent Configuration and Shared Logic

- Agent-specific config lives in `configs/`.
- Shared commands live in `commands/`.
- Skills are managed by the `skillex` utility and are stored in the `skills/` directory for versioning.
- Common personas and guidance live in `agents/`, `instructions/`, and related docs.

### Project Boundaries

- Cubicle manages agent setup, not project dependency installation.
- Project dependencies should remain project-local, such as `.venv`, `.bundle`, or `node_modules`.
- When behavior changes, update the `cubicle` script and the top-level docs together so the local workflow stays coherent.
