# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal Docker-based sandbox environment for running AI coding agents (Claude Code, Codex, and GitHub Copilot CLI) with full autonomy inside isolated containers. Each agent operates in its own container with 8GB memory and access to mounted host repositories and notes.

## Architecture

### Language-Specific Container Strategy

The project uses **language-specific agent containers** to handle dependencies for different programming environments. Each agent has base and language-specific variants:

**Container types:**
- **Base containers** (`claude-base`, `codex-base`): Common setup with git, SSH, MCP, GitHub CLI
- **Language containers** (`claude-python`, `claude-ruby`, `codex-python`, etc.): Extend base with language runtimes and package managers

**Why language-specific containers?**
- Projects share containers by language (e.g., all Python projects use `claude-python`)
- Language tooling (`uv`, `bundler`, `npm`) provides project isolation via `.venv`, `.bundle`, `node_modules`
- Fewer containers than per-project approach (6 language containers vs potentially dozens)
- Dependencies persist in mounted project directories

### Available Containers

**Claude Code:**
- `claude-python` - Python 3.9 + uv (modern package manager)
- `claude-ruby` - Ruby + bundler
- (Original `claude` container remains for Node.js/general use)

**Codex:**
- `codex-python` - Python 3.9 + uv
- `codex-ruby` - Ruby + bundler
- (Original `codex` container remains for Node.js/general use)

**GitHub Copilot CLI:**
- `copilot-python` - Python 3.11 + uv
- `copilot-ruby` - Ruby + bundler
- (Original `copilot` container remains for Node.js/general use)

**All containers share:**
- **Shared mounts**: `/cubicle/repos` (host: `/Users/jplatta/repos`) and `/cubicle/notes` (host: `/Volumes/Server/Notes/my_ken`)
- **Isolated configurations**: Each agent maintains its own config directory under `./config/`
- **Common resources**: SSH keys, git config, and GitHub credentials are mounted read-only
- **MCP integration**: Claude containers support MCP servers for extended capabilities

### Container Entry Scripts

Entry scripts are modular with shared base logic:
- `bin/entry-base.sh`: Common setup (SSH, git config, MCP servers) sourced by all containers
- `bin/entry-python.sh`: Sources base, adds Python-specific setup
- `bin/entry-ruby.sh`: Sources base, adds Ruby-specific setup

### Key Directories

```
agent-cubicle/
├── config/                      # Agent-specific configurations
│   ├── claude/                  # Claude Code config and plugins
│   ├── codex/                   # Codex config
│   └── copilot/                 # GitHub Copilot CLI config
├── bin/                         # Entry scripts
│   ├── entry-base.sh           # Common entry logic (sourced by all)
│   ├── entry-python.sh         # Python-specific setup
│   ├── entry-ruby.sh           # Ruby-specific setup
│   └── launch.sh               # CLI for launching agents in projects
├── doc/                         # Internal documentation and notes
├── Dockerfile.claude-base       # Base Claude container
├── Dockerfile.claude-python     # Claude + Python + uv
├── Dockerfile.claude-ruby       # Claude + Ruby + bundler
├── Dockerfile.codex-base        # Base Codex container
├── Dockerfile.codex-python      # Codex + Python + uv
├── Dockerfile.codex-ruby        # Codex + Ruby + bundler
├── Dockerfile.copilot-base      # Base Copilot container
├── Dockerfile.copilot-python    # Copilot + Python + uv
├── Dockerfile.copilot-ruby      # Copilot + Ruby + bundler
└── docker-compose.yml           # Orchestration configuration
```

### MCP Server Configuration

Claude Code container automatically configures three MCP servers on startup:
1. **obsidian-mcp**: Built from mounted source at `/obsidian-mcp`, provides Obsidian vault access
2. **todoist**: HTTP transport to `https://ai.todoist.net/mcp` (requires TODOIST_TOKEN)
3. **github**: HTTP transport to GitHub Copilot MCP API (requires GITHUB_TOKEN)

## Development Commands

### Launching Agents in Projects (Recommended)

Use the `bin/launch.sh` script to start language-specific containers:

```bash
# Launch Claude in a Python project
./bin/launch.sh claude-python my-python-project

# Launch Claude in a Ruby project
./bin/launch.sh claude-ruby my-rails-app

# Launch Codex in a Python project
./bin/launch.sh codex-python data-analysis

# Launch Copilot in a Python project
./bin/launch.sh copilot-python my-python-project

# Launch without specifying project (starts in /cubicle)
./bin/launch.sh claude-python
```

The script:
- Starts the appropriate language-specific container if not running
- Opens an interactive agent session in the specified project directory
- Automatically detects and validates available services

### Container Management

```bash
# Start language-specific containers
docker-compose up -d claude-python
docker-compose up -d claude-ruby
docker-compose up -d codex-python
docker-compose up -d copilot-python
docker-compose up -d copilot-ruby

# Start all containers (includes legacy containers)
docker-compose up -d

# Stop containers
docker-compose down

# Rebuild after Dockerfile changes
docker-compose build claude-python
docker-compose up -d claude-python

# View logs
docker-compose logs -f claude-python
```

### Direct Container Access

```bash
# Access language-specific Claude Code containers
docker exec -it claude-python-cubicle claude
docker exec -it claude-ruby-cubicle claude

# Access language-specific Codex containers
docker exec -it codex-python-cubicle codex
docker exec -it codex-ruby-cubicle codex

# Access language-specific Copilot containers
docker exec -it copilot-python-cubicle copilot
docker exec -it copilot-ruby-cubicle copilot

# Access container shell
docker exec -it claude-python-cubicle bash
```

### Working with Project Dependencies

Language tooling provides project isolation:

**Python projects (using uv):**
```bash
# Inside claude-python, codex-python, or copilot-python container
cd /cubicle/repos/my-python-project
uv venv                          # Create .venv in project dir
uv pip install -r requirements.txt
uv run pytest                    # Run tests in isolated env
```

**Ruby projects (using bundler):**
```bash
# Inside claude-ruby, codex-ruby, or copilot-ruby container
cd /cubicle/repos/my-ruby-project
bundle install --path .bundle    # Install gems locally
bundle exec rspec                # Run tests with project gems
```

**Node projects (using npm):**
```bash
# Inside any container (Node.js available in all base images)
cd /cubicle/repos/my-node-project
npm install                      # Creates node_modules locally
npm test                         # Uses project dependencies
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

Modify `bin/entry-base.sh` to add MCP servers at container startup. The base entry script is sourced by all language-specific containers. Use conditional checks to avoid duplicate registrations:

```bash
if ! claude mcp list 2>/dev/null | grep -q "server-name"; then
  claude mcp add --transport stdio server-name command args...
fi
```

### Adding New Language Containers

To add support for a new language (e.g., Go, Rust):

1. **Create base Dockerfile** (if not using existing agent base):
   ```dockerfile
   # Already exists: Dockerfile.claude-base, Dockerfile.codex-base
   ```

2. **Create language-specific Dockerfile:**
   ```dockerfile
   # Dockerfile.claude-go
   FROM agent-cubicle-claude-base:latest
   USER root
   RUN apt-get update && apt-get install -y golang-go && rm -rf /var/lib/apt/lists/*
   COPY bin/entry-go.sh /entry.sh
   RUN chmod +x /entry.sh && chown claude:claude /entry.sh
   USER claude
   CMD ["/entry.sh"]
   ```

3. **Create language entry script:**
   ```bash
   # bin/entry-go.sh
   #!/bin/bash
   source /entry-base.sh
   echo "Go environment:"
   go version
   tail -f /dev/null
   ```

4. **Add service to docker-compose.yml:**
   ```yaml
   claude-go:
     build:
       context: .
       dockerfile: Dockerfile.claude-go
     container_name: claude-go-cubicle
     # ... same volumes and config as other claude containers
   ```

5. **Update this documentation** with the new language container

## Design Principles

This environment prioritizes:
1. **Isolation**: Agents run in containers with full permissions but cannot affect the host
2. **Shared workspace**: All agents can collaborate on the same repositories
3. **Configuration versioning**: All agent configs are version-controlled
4. **Rapid iteration**: Easy to test new commands, skills, and prompts across models
5. **Full autonomy**: Containers run with "allow everything" mode for experimentation
6. **Language tooling over Docker layers**: Use native package managers (uv, bundler, npm) for project isolation instead of baking dependencies into images

## Project Isolation Strategy

**How dependencies work:**
- Each project maintains its own dependency directory (`.venv`, `.bundle`, `node_modules`) inside `/cubicle/repos/<project>/`
- These directories are part of the mounted volume, so they persist across container restarts
- Multiple projects can use the same language container without conflicts
- When you delete and recreate a container, projects simply reinstall dependencies (typically fast due to caching)

**Example workflow:**
1. Start `claude-python` container: `./bin/launch.sh claude-python my-django-app`
2. Agent creates virtual environment: `uv venv` (creates `/cubicle/repos/my-django-app/.venv`)
3. Agent installs dependencies: `uv pip install -r requirements.txt`
4. Dependencies persist in mounted volume even if container is recreated
5. Switch to another Python project in the same container: `cd ../another-python-project && uv venv`

## Future Workflow Goals

The owner plans to build:
- ✅ **A CLI for launching specific agents in specific repositories** (implemented as `bin/launch.sh`)
- Agents that pull tasks from Todoist, complete them, and open pull requests
- Multi-agent collaboration on projects (e.g., options trading dashboard)
- Delegation to cloud-based agents
