# Agent Cubicle

My sandboxed Docker environment for running AI coding agents with full autonomy.

## Why I Built This

I wanted to run AI coding agents (Claude Code, Codex, GitHub Copilot CLI) in "dangerously allow everything" mode without worrying about them breaking my host system. These containers let me give the agents full permissions to modify code, run commands, and work completely autonomously while keeping my main system safe.

## What I'm Running

- **Claude Code** - Running with complete autonomy, no safety rails
- **Codex** - Full unrestricted access to do whatever it needs
- **GitHub Copilot CLI** - Fully autonomous mode

Each agent gets:
- 8GB memory to do real work
- Access to my repos and notes (mounted from host)
- Complete permissions inside their container
- Shared workspace so they can all work on the same code

## The Setup

Each agent has its own isolated container where I can let it run wild. They all share access to my repositories and notes, so I can switch between agents or have them work on the same projects. No safety rails, no restrictions - just pure autonomous coding assistance in a safe sandbox.

## Quick Start

```bash
cp .env.example .env
# Add your API keys
docker-compose up -d
docker exec -it claude-code-workspace claude-code
```

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed instructions.