# Cubicle

Cubicle is my local harness for running coding agents with repo-managed configs, skills, commands, hooks, and prompts.

## Why I Built This

- Keep agent configuration and shared context under version control.
- Reuse the same skills, commands, and prompts across multiple agents.
- Launch agents in local project directories without copying config by hand.
- Make it easy to change how the setup works as my workflow evolves.

## What It Manages

Agents:
- Claude Code
- Codex
- GitHub Copilot CLI
- Gemini

Shared assets:
- agent configs in `configs/`
- reusable skills in `skills/`
- shared commands in `commands/`
- hook scripts in `hooks/`
- prompts, notes, and agent guidance in the rest of the repo

## Quick Start

```bash
cp .env.example .env
# add your API keys and PROJECTS_DIR
./cubicle help
./cubicle run --agent claude --project cubicle
```

The `cubicle` CLI installs the expected symlinks into each agent's dotfolder and then launches the chosen agent directly from the target project directory.

Useful commands:

```bash
./cubicle run --agent codex --project my-project
./cubicle init-hooks --agent claude
./cubicle clean --agent gemini
```

## Notes

- `PROJECTS_DIR` must be set in `.env`.
- Existing files in managed target locations are backed up under `~/.cubicle/backups/` before Cubicle replaces them with symlinks.
- Project dependencies remain project-local, such as `.venv`, `.bundle`, or `node_modules`.

## Next Steps (for me)

- Build a workflow where agents pull tasks from Todoist, complete them, and open a pull request.
- Expand the local CLI as the main entrypoint for project-specific agent workflows.
- Test whether agents can collaborate on an options trading dashboard in Streamlit, using my matplotlib prototypes.
- Delegate work to cloud agents when that becomes useful.
