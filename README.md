# Cubicle

Cubicle is a local harness and management tool for AI coding agents. It provides a central place to manage shared logic, configuration, and tools for different agent families (like Claude, Antigravity, and Codex), ensuring a consistent and observable developer experience.

The goal of Cubicle is to eliminate duplication across different agent setups and provide a single interface for extending agent capabilities.

## Current Features

### 1. Unified Telemetry Harness
A standardized way to capture and normalize usage data across different LLM families, storing everything in a central local SQLite database.

- **Event Normalization:** Maps agent-specific lifecycle events (e.g., `BeforeTool`, `PreToolUse`) to a consistent standard.
- **Centralized Storage:** A SQLite database at `~/.cubicle/data/telemetry.db` for easy querying of agent activity.
- **Passive Observation:** Non-blocking hook implementation that doesn't interfere with agent performance.

## Setup Guide

### 1. Prerequisite
Ensure you have Python 3.11+ installed on your system.

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
# Setup for Antigravity
cubicle init-hooks --agent agy

# Setup for Claude
cubicle init-hooks --agent claude

# Setup for Codex
cubicle init-hooks --agent codex
```

This command installs stable hook scripts to `~/.cubicle/hooks/` and automatically registers them in your agent's global settings (e.g., `~/.claude/settings.json`).

### Supervisor (early foundation)

Run `cubicle init` to create the local backlog, context, logs, runs, artifacts, and
versioned supervisor resources under `~/.cubicle`. Existing configuration is preserved.
`cubicle supervisor` starts Codex by default; set `supervisor.backend` in
`~/.cubicle/config.yaml` or pass `--backend claude`, `--backend agy`, or
`--backend codex` to select a CLI. Codex is given a local Cubicle MCP server;
other supervisor backends need their MCP configuration set separately.

Cubicle's initial MCP tools create and inspect shared Markdown backlog items and
PostgreSQL task graphs, and can start experimental host worker runs. Configure
`CUBICLE_DATABASE_URL` in the environment or `~/.cubicle/.env` and run
`cubicle db-init` once. Use a URL such as
`postgresql+psycopg://USER:PASSWORD@localhost:5432/cubicle`; never commit credentials.
Use a dedicated database role when available. The schema initializer refuses existing
unversioned Cubicle tables and migrates supported earlier Cubicle schema versions.

The host stdio server is `cubicle mcp --enable-workers`. Worker dispatch deliberately
uses the agent CLI's unattended permission-bypass mode; the node scope is an instruction,
not an enforced filesystem boundary. Worker output is stored under `~/.cubicle/runs` and
reconciled after process completion. Hook records are spooled and retried, and startup
checks incomplete runs without relaunching them. Unknown outcomes require investigation.
Graph snapshots and verified merged-branch cleanup are available; reliable termination
of independently detached descendants is not implemented.
To ask the supervisor to review long-running nodes, set
`limits.max_run_seconds` to a positive number in `~/.cubicle/config.yaml`.
The signal is checked when the supervisor polls a run; it does not stop a worker.
Claude nodes default to 30 agent turns; set `limits.claude_max_turns` or pass a
different `max_turns` when starting a node. Specify `model` there when needed.
An interactive `cubicle supervisor --backend agy` captures quota readings from the
Antigravity status line. Antigravity worker dispatch pauses when a reported quota
bucket reaches `limits.agy_max_used_percent` (default 80), or its reading is older
than five minutes. The status line may need a model request before it has quota data.
The check is account-wide, conservative across reported buckets, and applies before
dispatch; it cannot reserve capacity or stop other applications from using the quota.
Codex worker dispatch checks its current account windows through the Codex app server
and pauses at `limits.codex_max_used_percent` (default 80), or if the reading is
unavailable. Active-run polls flag a quota threshold or unavailable reading for the
supervisor to investigate. These checks do not reserve quota or automatically stop
running workers. Claude subscription-window gating is deferred.
Raw prompts and event payloads may contain credentials or other sensitive data and are
stored in the local spool and database without comprehensive redaction. Restrict access
to those locations and do not use secrets you cannot safely expose there. Use only for
supervised experiments; do not rely on it for unattended production work.

The Compose service runs MCP on loopback port 8765 and connects to the existing PostgreSQL
instance; set `CUBICLE_DATABASE_URL` with `host.docker.internal` as its host and run
`docker compose up -d cubicle-mcp`. Worker launch is disabled in that container: workers
must run on the host. The HTTP endpoint has no authentication and must remain local. For an isolated alternative, `docker compose --profile standalone up -d postgres`
starts a separate PostgreSQL on loopback port 55432 with a named volume; set
`CUBICLE_STANDALONE_POSTGRES_PASSWORD` first. Choose the intended database URL explicitly;
Compose never starts or modifies quant-infra services.

### Commands

- `cubicle init-hooks [--agent <name>] [--force]`: Initializes centralized resources and/or registers hooks for an agent. Use `--force` to refresh code and reset the database.
- `cubicle del-hooks --agent <name>`: Unregisters hooks from the specified agent.
- `cubicle set-env NAME VALUE`: Stores a shared env var in `~/.cubicle/.env` for Cubicle-launched agents.
- `cubicle unset-env NAME`: Removes a shared env var from `~/.cubicle/.env`.
- `cubicle list-env`: Prints the shared env vars stored in `~/.cubicle/.env`.
- `cubicle claude [args...]`: Exec the upstream `claude` CLI, forwarding all trailing args and setting `CUBICLE_LLM_FAMILY=claude` plus any shared vars from `~/.cubicle/.env` for that process tree.
- `cubicle agy [args...]`: Exec the upstream `agy` CLI, forwarding all trailing args and setting `CUBICLE_LLM_FAMILY=agy` plus any shared vars from `~/.cubicle/.env` for that process tree.
- `cubicle codex [args...]`: Exec the upstream `codex` CLI, forwarding all trailing args and setting `CUBICLE_LLM_FAMILY=codex` plus any shared vars from `~/.cubicle/.env` for that process tree.
- `cubicle help`: Shows this help message.

## Telemetry Usage

Once initialized, Cubicle captures tool use, prompt submission, and session events in the background.

### Agent Launch Wrappers
Use the Cubicle wrappers when starting supported agent CLIs so the telemetry hook can identify the agent family reliably:

```bash
cubicle claude --help
cubicle agy
cubicle codex exec "summarize the repo"
```

Cubicle sets `CUBICLE_LLM_FAMILY` in the launched process environment and then hands off with an exec-style launch. The variable only exists in that process tree; it does not persist in your shell after the command exits.

If `~/.cubicle/.env` exists, Cubicle also loads those shared env vars into the launched agent process. This is the supported way to provide shared credentials or tool configuration to agents, MCP servers, and child tools started from a Cubicle wrapper.

Manage the file with:

```bash
cubicle set-env OPENAI_API_KEY sk-...
cubicle set-env ANTHROPIC_API_KEY some-value
cubicle list-env
cubicle unset-env ANTHROPIC_API_KEY
```

Direct agent launches outside the wrapper are treated as `unknown` unless `CUBICLE_LLM_FAMILY` is already set externally.

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
