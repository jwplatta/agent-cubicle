# Cubicle

This is my personal, sandboxed Docker setup for running AI coding agents with full autonomy.

## Why I Built This

- I want one place to store and version my configs, shared context, and examples.
- I want to be able to iterate quickly on commands, skills, prompts across multiple models.
- I want to learn what these agents can and cannot do for me.
- I want to run agents in “allow everything” mode without risking my host system.

## What It Runs

Agents:
- Claude Code
- Codex
- GitHub Copilot CLI

Each agent gets:
- 8GB memory
- Access to my repos and notes (mounted from the host)
- Full permissions inside its container
- A shared workspace so they can work on the same code

## Quick Start

```bash
cp .env.example .env
# add your API keys
docker-compose up -d
docker exec -it claude-cubicle claude
```

See `DOCKER_SETUP.md` for the detailed setup.

## Next Steps (for me)

- Build a workflow where agents pull tasks from Todoist, complete them, and open a pull request. Document that in `CLAUDE.md` and `AGENTS.md`.
- Build a CLI to run a specific agent in a specific repo.
- Test whether agents can collaborate on an options trading dashboard in Streamlit, using my matplotlib prototypes.
- Delegating to cloud agents
