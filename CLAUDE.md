# CLAUDE.md

This file provides guidance to Claude Code (`claude.ai/code`) when working with code in this repository.

## Project Overview

Cubicle is a local harness for coding agents. It keeps shared configuration, skills, commands, hooks, prompts, and notes in one repo, then uses the `./cubicle` CLI to symlink the right files into each agent's home directory before launching that agent inside a local project.

## Primary Workflow

Create `.env` from `.env.example`, set `PROJECTS_DIR`, then use the local CLI:

```bash
./cubicle help
./cubicle run --agent claude --project cubicle
./cubicle init-hooks --agent claude
./cubicle clean --agent claude
```

Behavior:
- `run` loads `.env`, validates `PROJECTS_DIR`, installs managed symlinks, then launches the selected agent from `${PROJECTS_DIR}/<project>`.
- `init-hooks` installs the shared hook scripts into the agent's home directory.
- `clean` removes symlinks that point back into this repo.
- Existing files at managed targets are moved under `~/.cubicle/backups/<run-id>/` before symlinks are created.

## Key Directories

```text
cubicle/
├── configs/      # Agent-specific config files
├── skills/       # Shared skills linked into agent home directories
├── commands/     # Shared command markdown linked into agent home directories
├── hooks/        # Shared local hook scripts
├── agents/       # Agent personas and repo guidance
├── prompts/      # Reusable prompt templates
├── doc/          # Internal notes and design docs
└── cubicle       # Local CLI entrypoint
```

## Config and Link Management

Cubicle manages these agent-specific targets:

- Claude: `configs/claude/settings.json` -> `~/.claude/settings.json`
- Codex: `configs/codex/config.toml` -> `~/.codex/config.toml`
- Gemini: `configs/gemini/settings.json` and `configs/gemini/trusted_hooks.json`
- Copilot: `configs/copilot/config.json`

Shared directories:
- Each entry in `skills/` is symlinked into the matching agent home `skills/` directory.
- Each file in `commands/` is symlinked into the matching agent home `commands/` directory.
- Hooks are linked from `hooks/` into the agent home `hooks/` directory.

## Working With Projects

Project dependencies should stay inside the project being worked on:

- Python: use `uv venv`, `uv pip install`, `uv run pytest`
- Ruby: use `bundle install`, `bundle exec rspec`
- Node: use `npm install`, `npm test`

Cubicle should not own per-project dependency state beyond launching the agent in the right project directory.

## Commit Messages

- Use lowercase, imperative mood for the subject line.
- Keep the subject line under 72 characters.
- Do not end the subject line with a period.
- Use the body to explain what changed and why when a body is warranted.
- Include `Co-Authored-By: jwplatta <jwplatta@users.noreply.github.com>`.

## Environment Notes

- `.env` is required and must set `PROJECTS_DIR`.
- API keys remain local environment concerns rather than repo-tracked config.
- If new shared assets are added, prefer extending the `cubicle` script rather than adding one-off setup steps.
