# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal Docker-based sandbox environment for running AI coding agents (Claude Code, Codex, and GitHub Copilot CLI) with full autonomy inside isolated containers. Each agent operates in its own container with 8GB memory and access to mounted host repositories and notes.

## Architecture

### Container Structure

Three separate Docker containers run concurrently, each with:
- **Shared mounts**: `/cubicle/repos` (host: `/Users/jplatta/repos`) and `/cubicle/notes` (host: `/Volumes/Server/Notes/my_ken`)
- **Isolated configurations**: Each agent maintains its own config directory under `./config/`
- **Common resources**: SSH keys, git config, and GitHub credentials are mounted read-only
- **MCP integration**: All containers support MCP servers for extended capabilities

Container entry points:
- `bin/entry-claude.sh`: Installs obsidian-mcp, configures MCP servers (Todoist, GitHub, Obsidian)
- `bin/entry-codex.sh`: Basic initialization
- `bin/entry-copilot.sh`: GitHub Copilot CLI setup

### Key Directories

```
agent-cubicle/
├── config/               # Agent-specific configurations
│   ├── claude/          # Claude Code config and plugins
│   ├── codex/           # Codex config
│   └── copilot/         # GitHub Copilot CLI config
├── bin/                 # Entry scripts for each container
├── doc/                 # Internal documentation and notes
├── Dockerfile.claude    # Claude Code container
├── Dockerfile.codex     # Codex container
├── Dockerfile.copilot   # GitHub Copilot CLI container
└── docker-compose.yml   # Orchestration configuration
```

### MCP Server Configuration

Claude Code container automatically configures three MCP servers on startup:
1. **obsidian-mcp**: Built from mounted source at `/obsidian-mcp`, provides Obsidian vault access
2. **todoist**: HTTP transport to `https://ai.todoist.net/mcp` (requires TODOIST_TOKEN)
3. **github**: HTTP transport to GitHub Copilot MCP API (requires GITHUB_TOKEN)

## Development Commands

### Container Management

```bash
# Start all containers
docker-compose up -d

# Start individual containers
docker-compose up -d claude
docker-compose up -d codex
docker-compose up -d copilot

# Stop containers
docker-compose down

# Rebuild after Dockerfile changes
docker-compose up -d --build

# View logs
docker-compose logs -f <service-name>
```

### Accessing Agents

```bash
# Claude Code (interactive)
docker exec -it claude-cubicle claude

# Codex (interactive)
docker exec -it codex-cubicle codex

# GitHub Copilot CLI (interactive)
docker exec -it copilot-cubicle copilot

# Access container shell
docker exec -it <container-name> bash
```

### Working with Specific Repositories

All containers mount `/Users/jplatta/repos` to `/cubicle/repos`. To work on a specific repository:

```bash
# Claude Code in a specific repo
docker exec -it claude-cubicle bash -c "cd /cubicle/repos/my-project && claude"

# Codex in a specific repo
docker exec -it codex-cubicle bash -c "cd /cubicle/repos/my-project && codex"
```

### MCP Server Management (Claude Code)

```bash
# List configured MCP servers
docker exec -it claude-cubicle claude mcp list

# Add a new MCP server (stdio transport)
docker exec -it claude-cubicle claude mcp add --transport stdio <name> <command> [args...]

# Add a new MCP server (HTTP transport with auth)
docker exec -it claude-cubicle claude mcp add --header "Authorization: Bearer <token>" --transport http <name> <url>
```

## Environment Configuration

### Required Environment Variables

Create `.env` from `.env.example`:

```bash
ANTHROPIC_API_KEY=<your-key>           # Required for Claude Code
GITHUB_TOKEN=<your-token>              # Required for Copilot CLI and MCP GitHub server
COPILOT_TOKEN=<your-token>             # GitHub token for Copilot container
TODOIST_TOKEN=<your-token>             # Optional: Todoist MCP integration
OPENAI_API_KEY=<your-key>              # Optional: For Codex if using OpenAI
```

### Adding New MCP Servers

Modify `bin/entry-claude.sh` to add MCP servers at container startup. Use conditional checks to avoid duplicate registrations:

```bash
if ! claude mcp list 2>/dev/null | grep -q "server-name"; then
  claude mcp add --transport stdio server-name command args...
fi
```

## Design Principles

This environment prioritizes:
1. **Isolation**: Agents run in containers with full permissions but cannot affect the host
2. **Shared workspace**: All agents can collaborate on the same repositories
3. **Configuration versioning**: All agent configs are version-controlled
4. **Rapid iteration**: Easy to test new commands, skills, and prompts across models
5. **Full autonomy**: Containers run with "allow everything" mode for experimentation

## Future Workflow Goals

The owner plans to build:
- Agents that pull tasks from Todoist, complete them, and open pull requests
- A CLI for launching specific agents in specific repositories
- Multi-agent collaboration on projects (e.g., options trading dashboard)
- Delegation to cloud-based agents
