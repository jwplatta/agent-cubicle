# Set up and use Cubicle

Cubicle runs the supervisor and its workers on your machine. PostgreSQL stores task
graphs and events; the shared backlog, configuration, deployed prompts and run files
live under `~/.cubicle`. The default supervisor is Codex.

## 1. Prerequisites

- Python 3.11 or newer, Git, and the `uv` package manager (or a Python environment
  where you can install the package).
- A running PostgreSQL instance with a **separate `cubicle` database** and a user
  allowed to create and alter tables in that database.
- Codex CLI installed and signed in. Install and sign in to Claude Code or
  Antigravity (`agy`) if you want to use those workers or supervisors.
- GitHub CLI (`gh`), signed in with access to the repositories where workers will
  open pull requests.

Check what is available with `python3 --version`, `git --version`, `codex --version`,
and `gh auth status`; use `claude --version` or `agy --version` if applicable.
You do not need Docker when using an existing PostgreSQL instance.

On the machine where this guide was written, Cubicle is already installed from
`~/repos/cubicle`, and a separate `cubicle` database and connection in
`~/.cubicle/.env` have already been configured on the existing PostgreSQL instance.
Do not create a second database or overwrite that connection just to repeat setup.

## 2. Install the CLI

From your existing checkout, install in editable mode using Python 3.11:

```sh
cd ~/repos/cubicle
uv tool install --python 3.11 --editable .
cubicle --help
```

If `cubicle` is not found, run `uv tool update-shell`, open a new shell, and retry.
Alternatively, create a Python 3.11 virtual environment, run `pip install -e .`
inside it, and activate that environment whenever you use Cubicle. For a fresh
checkout elsewhere, clone `https://github.com/jwplatta/agent-cubicle.git` first.

## 3. Initialize the home directory

```sh
cubicle init
```

This creates missing directories including `backlog`, `context`, `logs`, `runs`,
`artifacts`, and `resources` under `~/.cubicle`, and deploys versioned supervisor
and worker instructions. It preserves an existing `config.yaml` and existing data.

## 4. Connect PostgreSQL and initialize the schema

For the existing machine setup, first check that the PostgreSQL service is running,
then run:

```sh
cubicle db-init
```

This uses `CUBICLE_DATABASE_URL` from the environment or `~/.cubicle/.env` and
creates or upgrades Cubicle's supported schema. It does not create the PostgreSQL
database or database role. Keep Cubicle in its own database; do not point it at the
database used by another application.

For a new installation, create a separate database and role using your PostgreSQL
administration workflow. Then put a connection URL in `~/.cubicle/.env` using a
private editor and set the file permissions to `600`. The format is:

```text
CUBICLE_DATABASE_URL="postgresql+psycopg://USER:PASSWORD@localhost:5432/cubicle"
```

Replace the placeholders with your own connection details, URL-encoding special
characters in the username or password. Then run `cubicle db-init`. Do not commit
the file or paste its contents into a chat. `cubicle set-env NAME VALUE` is also
available, but entering a secret directly in a command can leave it in shell history;
`cubicle list-env` prints stored values, including secrets.

### Optional: separate Docker PostgreSQL

If you don't have an existing instance and have Docker running, from the repository:

```sh
export CUBICLE_STANDALONE_POSTGRES_PASSWORD='choose-a-private-password'
docker compose --profile standalone up -d postgres
```

This starts a separate PostgreSQL on `127.0.0.1:55432`, with database and user both
named `cubicle` and a named Docker volume. Configure `~/.cubicle/.env` with the URL
`postgresql+psycopg://cubicle:PASSWORD@localhost:55432/cubicle`, using the chosen
password, then run `cubicle db-init` on the host. The example password command can
appear in shell history; use a private way to supply a real password. Compose does
not start or modify the separate quant-infra services.

## 5. Install hooks

Register hooks for each installed CLI you intend Cubicle to use:

```sh
cubicle init-hooks --agent codex
cubicle init-hooks --agent claude
cubicle init-hooks --agent agy
```

Skip agents you have not installed. These commands copy Cubicle's hook scripts to
`~/.cubicle/hooks` and register them in the corresponding agent configuration; they
do not install or authenticate the agent CLIs. Hook failures are reported in
`~/.cubicle/logs/hooks.log` and on stderr. Provider-specific hook coverage differs.

## 6. Start the supervisor

```sh
cubicle supervisor
```

This starts Codex and supplies its Cubicle MCP server automatically. To select a
different installed supervisor for one session:

```sh
cubicle supervisor --backend claude
cubicle supervisor --backend agy
```

Claude receives a per-session Cubicle MCP configuration; agy registers a Cubicle
server in its global MCP configuration while preserving unrelated servers. If a
different server already uses the name `cubicle`, agy startup stops and reports the
conflict. The CLIs may show first-run trust or bypass-mode confirmation screens.

To set the default persistently, edit `~/.cubicle/config.yaml` and add or change:

```yaml
supervisor:
  backend: codex  # codex, claude, or agy
```

Cubicle launches agents with permission bypass on the host, as requested for
unattended work. Node scopes are instructions, not filesystem isolation. Review
the repository and configuration before allowing a supervisor or worker to operate.

## 7. Plan and run your first task

In the supervisor conversation, try:

> Inspect the shared backlog. Help me define a small task for `~/repos/MY_REPO`,
> including its goal and acceptance checks. Add it to the Cubicle backlog, but
> don't start work until we've reviewed the plan.

After reviewing the plan, ask the supervisor to mark it ready, create a task graph,
and run the first bounded node. Ask it to show the graph and progress. For coding
work, ask it to use a task worktree and open a pull request for your review. Cubicle
considers the task complete only after the PR is merged and the local task branch
is safely cleaned up; for non-coding work, you confirm completion.

The Markdown backlog is in `~/.cubicle/backlog`. Run files and captured output are
in `~/.cubicle/runs`; managed tasks, graphs, runs and events are in PostgreSQL.
Cubicle's MCP tools are how the supervisor reads and updates them. Skillex and the
project-backlog skill can be used when installed, but Cubicle does not require a
specific private skills repository.

## Usage and progress controls

Add or edit these keys under `limits` in `~/.cubicle/config.yaml` as needed:

```yaml
limits:
  max_run_seconds: 600          # supervisor review signal, not a hard timeout
  claude_max_turns: 30          # per-node default; can be overridden at dispatch
  codex_max_used_percent: 80    # pause new Codex workers at this account usage
  agy_max_used_percent: 80      # pause new agy workers at this account usage
```

The supervisor must poll a run to see the elapsed-time or usage review signal;
neither automatically cancels a worker. Codex checks account usage before dispatch.
For agy, start an interactive agy supervisor and make a request so its status line
can provide a quota reading. New agy worker dispatch pauses if that reading is over
five minutes old or any reported bucket is at the threshold. These account-wide
checks cannot reserve usage or stop other clients. Claude subscription usage is not
gated; its turn limit and the common check-in are the current controls.

## Troubleshooting and data handling

- **Database connection fails:** Check that PostgreSQL is running, the URL points to
  the dedicated Cubicle database, and the database role has the required permissions.
  Rerun `cubicle db-init` after fixing the connection.
- **A worker won't start because of usage:** Check the configured threshold and the
  provider's usage display. For agy, refresh an interactive status-line reading. A
  missing or stale reading pauses dispatch rather than assuming usage is zero.
- **A run is unknown after interruption:** Ask the supervisor to inspect the run,
  its process and output, and any external side effects. It can record reviewed
  evidence with `resolve_unknown_run`; Cubicle does not automatically rerun it.
- **Events are missing:** Check `~/.cubicle/logs/hooks.log`, the agent's hook
  configuration, and the run's hook spool. Restarting the host MCP server retries
  spooled events. Hosted tools and provider internals may not emit local hooks.
- **Sensitive data:** Cubicle redacts known environment secrets and common credential
  patterns in newly captured worker output and hooks, but detection is not complete.
  Existing logs are not rewritten, and backlog/task text may contain sensitive data.
  Keep the home directory and database private.

## Optional: containerized MCP

The supervisor normally starts a host MCP server automatically; no separate MCP
container is needed for host workers. If you want an HTTP MCP service for other
local clients, set `CUBICLE_DATABASE_URL` in the Compose environment with a host
of `host.docker.internal`, then run `docker compose up -d cubicle-mcp` from the
checkout. The endpoint binds to `127.0.0.1:8765` and has no authentication. Worker
launch is disabled in the container; the host server is required to dispatch workers.
