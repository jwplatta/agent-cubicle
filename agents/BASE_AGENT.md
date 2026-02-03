## Workflow

1. **Setup**: Create a new worktre and feature branch from main unless the user says to work on the main branch without committing (see [Git Branch Management](#git-branch-management))

```sh
# Create a new worktree with a new branch
git worktree add ../project-feature-a -b feature/a

# Or create a worktree with an existing branch
git worktree add ../project-fix fix/123
```

2. If user prompt provided, break prompt down into tasks.
3. If user prompt is similar to "next task", then select next task from Todoist (see [Task Selection](#task-selection))
4. **Implement**: Follow repo-specific guidelines (check README.md, CONTRIBUTING.md, CLAUDE.md)
   1. Write todos and notes and context to Obsidian (see [Knowledge Management](#knowledge-management))
   2. Reference repo guidelines for language-specific standards
5. **Quality**:
   - Run linter and fix issues before committing
   - Write minimal unit tests covering core functionality. Tests should focus on core logic, not exhaustive coverage.
6. **Delivery**: Use GitHub CLI to push branch and create pull request
7. When you're done pushing the pull request then remove the worktree:
```sh
git worktree remove ../project-feature-a
```

## Git Branch Management
- **Never commit directly to main**
- Always create a new branch from main using prefixes:
  - `feature/` - new functionality
  - `fix/` - bug fixes
  - `chore/` - maintenance tasks
  - `refactor/` - code restructuring
- Commit messages should be short and start with a verb, e.g. "refactored", "fixed", "added", "removed", etc.

## Task Selection
If no specific task is provided:
1. Check Todoist "Automated Trading" project
2. Look in the "Today" section
3. Find tasks tagged with `claude-code`
4. Read the selected task and create an implementation checklist

## Knowledge Management
- **Obsidian Vault**: Use `my_ken` vault for context and notes
  - When needed, search vault for task-related context referenced in Todoist
  - Write notes and todo lists to `/Contexts` folder when compacting context window
  - Document decisions and implementation details as needed to the `/Contexts` folder
  - Be sure to keep context notes organized for future reference with frontmatter that includes tags with keywords:

```markdown
---
tags:
created_date:
---
```