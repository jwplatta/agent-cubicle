# Gemini Project: Cubicle

## Project Overview

"Cubicle" is a single harness designed to provide shared logic, configuration, and tools for LLM coding agents. It offers a consistent, sandboxed environment for running various agents (e.g., Claude, Codex, Gemini) with a unified set of skills, prompts, and workflows.

The goal is to minimize duplication and maximize the effectiveness of AI agents by centralizing:
- **Shared Skills:** Reusable tools and functions accessible across different models.
- **Unified Configuration:** Consistent system prompts, environment variables, and operational boundaries.
- **Isolated Execution:** A Docker-based infrastructure that ensures agents operate safely and predictably without affecting the host system.
- **Interoperability:** A common framework for agents to interact with version control, file systems, and external APIs.

## Building and Running

### Prerequisites

- Docker
- An `.env` file with the necessary API keys (see `.env.example`)

### Key Commands

- **Build and start all services (in the background):**
  ```bash
  docker-compose up -d
  ```

- **Run a specific agent:**
  - **Claude:**
    ```bash
    docker exec -it claude-cubicle claude
    ```
  - **Codex:**
    ```bash
    docker exec -it codex-cubicle codex
    ```
  - **Copilot:**
    ```bash
    docker exec -it copilot-cubicle copilot
    ```

- **Run language-specific agents:**
  - **Claude (Python):**
    ```bash
    docker exec -it claude-python-cubicle claude
    ```
  - **Claude (Ruby):**
    ```bash
    docker exec -it claude-ruby-cubicle claude
    ```
  - **And so on for other language-specific containers...**

- **Stop and remove all services:**
  ```bash
  docker-compose down
  ```

## Development Conventions

### Agent Configuration & Shared Logic

- **Agent-Specific Config:** Located in the `configs/` directory (e.g., `configs/claude`, `configs/gemini`).
- **Shared Skills:** Reusable agent capabilities are defined in the `skills/` directory.
- **Shared Instructions:** Common personas and system prompts are in the `instructions/` or `agents/` directories.
- **Prompts:** Common prompt templates are stored in `prompts/`.
- **Workflow Documentation:** `CLAUDE.md` and `GEMINI.md` serve as living documentation for agent-specific workflows and repo-wide guidance.

### Docker Environment

- The Dockerfiles for each agent are in the root of the project (e.g., `Dockerfile.claude`, `Dockerfile.codex`).
- These Dockerfiles define the base environment for each agent, including system dependencies, user setup, and the installation of necessary tools and libraries.
- The `entry-*.sh` scripts in the `bin` directory are the entry points for the containers. They handle the initial setup of the container environment, including SSH configuration, Git setup, and the installation of any project-specific tools.
