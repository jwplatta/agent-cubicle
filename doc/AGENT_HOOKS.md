# Agent Hooks

## Goal

I want to develop a set of hooks that allow me to capture agent input/output so that I can begin to detect useful patterns in my usage of LLMs.

## Description

- We want to write the hooks as either bash or python. These hooks should out json with all the information and we should then store that information in a sqlite database.
- Information we want to broadly capture. We want to error on the side of capturing too much right now:
  - User input
  - Context
  - Tool request input
  - Tool useage output
  - Metadata about the output - lenght, time, etc.
  - Plan mode or implementation
  - timestamp
  - subagent usage
  - stop failures
  - instructions or context loading
  - mcp server usage
  - terminate / stop,
  - git worktree operations
  - task creation, completion, deletion,
  - file changes
- We want to store everything in a sqlite database that's easy to query later. We will need to design a suitable schema but at the very least it needs a column that captures the output json from the hook and a column with the cubicle defined event type and a column with the llm family (gemini, claud, codex), a column with the llm model, a timestamp, (maybe all thsi data will be included in the json output by the hook)
- Claude, Gemini, and Codex have different names for their hooks. We need a consistent naming convention internally for cubicle that maps to the claude, gemini, codex naming conventions.
- We will need to be able to install these hooks at the user level so they apply in all projects. So I believe they will need to go into `~/.gemini/hooks`, `~/.codex/hooks`, and `~/.claude/hooks`.
  - We should add a command to the cubicle CLI to basically do `$ cubicle --init-hooks --agent claude` or something like that
- We will eventually develop a dashboard to display some interesting stats on Agent usage

## Development

1. Review the documentation for gemini, claude, and codex to see how they're hook setups and naming conventions are different and similar.
  - Find naming conventions
  - Find which out what data each outputs.
  - Determine when we need to write separate hooks for gemini, claude, and codex and when they can share the same hook code
2. Create a single coherent hook naming convention that generalizes gemini, claude, and codex differences.
3. Define a sqlite database schema that is sufficient for storing and all the relevant data
4. Write the hooks code in this repo
5. Extend the cubicle CLI to install these hooks for each of the LLM tools (gemini, claude, codex)

## Reference

- Gemini hooks: https://geminicli.com/docs/hooks/
- Claude hooks: https://code.claude.com/docs/en/hooks
- Codex hooks: https://developers.openai.com/codex/hooks