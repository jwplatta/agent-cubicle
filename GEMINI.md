# Gemini Project: Cubicle

## Project Overview

This project, "Cubicle," is a sandboxed Docker environment for running and managing various AI coding agents. It provides a consistent and isolated space to experiment with different agents, including Claude, Codex, and GitHub Copilot, without affecting the host system.

The core of the project is a set of Docker services defined in `docker-compose.yml`. Each service runs a specific AI agent in its own container, with dedicated resources and a shared workspace. This allows for easy iteration on configurations, prompts, and skills across multiple models.

The environment is designed for full autonomy, with each agent having access to the user's repositories and notes (mounted as volumes). This enables them to perform tasks like reading and writing code, interacting with version control, and potentially even opening pull requests.

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

### Agent Configuration

- Agent-specific configurations are located in the `config` directory (e.g., `config/claude`, `config/codex`).
- Shared configuration and base agent instructions are in `config/shared`.
- The `CLAUDE.md` file in the root of the project is used as a place to document workflows and ideas for the agents.

### Docker Environment

- The Dockerfiles for each agent are in the root of the project (e.g., `Dockerfile.claude`, `Dockerfile.codex`).
- These Dockerfiles define the base environment for each agent, including system dependencies, user setup, and the installation of necessary tools and libraries.
- The `entry-*.sh` scripts in the `bin` directory are the entry points for the containers. They handle the initial setup of the container environment, including SSH configuration, Git setup, and the installation of any project-specific tools.
