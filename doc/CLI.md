# Agent CLI

This is a simple, local CLI to run my coding agents (Codex, Claude, Copilot, Gemini) while keeping all shared config, skills, commands, prompts, hooks, and other context in this repo (`agent-cubicle`). This is intentionally non-production code: it should be simple, intelligible, and easy to change as my needs evolve.

The CLI will manage symlinks from the repo into each agent's dotfolder and then run the selected agent in the target project directory.

## behavior

```sh
$ agent-cubicle run --agent claude --project agent-cubicle
```

- When this command runs, it should check all required symlinks for the chosen agent (configs, skills, commands).
- If a target path already exists and is not the expected symlink, stop and print a clear message telling the user to resolve the conflict.
- The script must load env vars from the local `.env` file (not committed).
- `PROJECTS_DIR` must be set (from `.env`). If it is missing, stop and tell the user to set it.
- Then run the selected agent with the working directory set to `${PROJECTS_DIR}/${project}`.

## configs by agent (symlink targets)

**Claude** symlink `./configs/claude/settings.json` to `~/.claude/settings.json`

**Codex** symlink `./configs/codex/config.toml` to `~/.codex/config.toml`

**Gemini** symlink `./configs/gemini/settings.json` to `~/.gemini/settings.json` and `./configs/gemini/trusted_hooks.json` to `~/.gemini/trusted_hooks.json`

**Copilot** symlink `./configs/copilot/config.json` to `~/.copilot/config.json` and `./configs/copilot/mcp-config.json` to `~/.copilot/mcp-config.json`

## shared links by agent

Symlink each entry inside `skills/` into the corresponding agent dotfolder (folders or files). For commands, symlink each file inside `commands/` (e.g., `./commands/command_name.md`) into `~/.<agent>/commands/`. Do not symlink the parent `skills/` or `commands/` folders themselves.

## implementation

Create a script in the repo root named `agent-cubicle.sh`. We will run it from this repo. It should support:

- `agent-cubicle run --agent <codex|claude|copilot|gemini> --project <name>`
- `agent-cubicle clean --agent <codex|claude|copilot|gemini>`
- `agent-cubicle help` (or `-h/--help`) with a brief description
