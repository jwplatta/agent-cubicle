# Docker Setup for AI Coding Agents

Run Claude Code, Codex, and GitHub Copilot CLI in Docker containers with access to your local repositories and notes.

## Setup

1. **Copy the environment file and add your API keys:**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   # Add GITHUB_TOKEN (required for GitHub Copilot CLI - fine-grained PAT with "Copilot Requests" permission)
   # Optionally add OPENAI_API_KEY for Codex if using OpenAI models
   ```

2. **Configure MCP servers (optional):**
   Edit `config/mcp_servers.json` to add or modify MCP servers. The default configuration includes:
   - Filesystem server with access to mounted repos and notes
   - GitHub server (requires GITHUB_TOKEN in .env)

3. **Build and run:**
   ```bash
   # Build and start all containers
   docker-compose up -d

   # Or start individual services
   docker-compose up -d claude-code
   docker-compose up -d codex
   docker-compose up -d copilot
   ```

4. **Access the agents:**
   ```bash
   # Claude Code
   docker exec -it claude-code-workspace claude-code

   # Codex
   docker exec -it codex-workspace codex

   # GitHub Copilot CLI (interactive mode)
   docker exec -it copilot-workspace copilot
   ```

## Memory Configuration

All containers are configured with:
- **Memory limit:** 8GB
- **Memory reservation:** 4GB

Adjust these in `docker-compose.yml` under `deploy.resources` if needed.

## Mounted Directories

Inside all containers:
- `/workspace/repos` → `/Users/jplatta/repos`
- `/workspace/notes` → `/Volumes/jwplatta/Server/Notes/my_ken`

Configuration directories:
- Claude Code: `./config` → `/root/.config/claude-code`
- Codex: `./config/codex` → `/root/.config/codex`
- GitHub Copilot CLI: `./config/github-copilot` → `/root/.config/github-copilot`

## Adding More MCP Servers

Edit `config/mcp_servers.json` to add more MCP servers. Example:

```json
{
  "mcpServers": {
    "your-server-name": {
      "command": "npx",
      "args": ["-y", "@your/mcp-server"],
      "env": {
        "YOUR_ENV_VAR": "${YOUR_ENV_VAR}"
      }
    }
  }
}
```

Then add any required environment variables to `.env`.

## Useful Commands

### General
- **Start all containers:** `docker-compose up -d`
- **Stop all containers:** `docker-compose down`
- **View logs:** `docker-compose logs -f [service-name]`
- **Rebuild after changes:** `docker-compose up -d --build`

### Claude Code
- **Access shell:** `docker exec -it claude-code-workspace bash`
- **Run Claude Code:** `docker exec -it claude-code-workspace claude-code`
- **View logs:** `docker-compose logs -f claude-code`

### Codex
- **Access shell:** `docker exec -it codex-workspace bash`
- **Run Codex:** `docker exec -it codex-workspace codex`
- **View logs:** `docker-compose logs -f codex`

### GitHub Copilot CLI
- **Access shell:** `docker exec -it copilot-workspace bash`
- **Run Copilot (interactive mode):** `docker exec -it copilot-workspace copilot`
- **Run Copilot (programmatic mode):** `docker exec -it copilot-workspace copilot -p "your prompt here"`
- **View logs:** `docker-compose logs -f copilot`

## Container Details

### Claude Code Container
- **Base image:** Node.js 20 (Debian Bullseye)
- **Dockerfile:** `Dockerfile.claude-code`
- **Entry point:** Runs `claude-code` by default
- **Configuration:** `/root/.config/claude-code`

### Codex Container
- **Base image:** Python 3.11 (Debian Bullseye Slim)
- **Dockerfile:** `Dockerfile.codex`
- **Package manager:** uv (fast Python package installer)
- **Configuration:** `/root/.config/codex`

### GitHub Copilot CLI Container
- **Base image:** Node.js 22 (Debian Bullseye)
- **Dockerfile:** `Dockerfile.copilot`
- **Entry point:** Uses `tail -f /dev/null` to keep container running
- **Configuration:** `/root/.config/github-copilot`
- **Authentication:** Uses GITHUB_TOKEN environment variable (fine-grained PAT with "Copilot Requests" permission)

## Notes

- SSH keys and git config are mounted read-only for git operations in all containers
- All containers have interactive TTY enabled for CLI usage
- MCP server configurations for Claude Code are loaded from `config/mcp_servers.json`
- All containers share the same repository and notes directories
- GitHub Copilot CLI requires an active GitHub Copilot subscription
- On first run, GitHub Copilot CLI may prompt for authentication via `/login` command if token authentication fails
