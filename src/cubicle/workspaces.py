"""Create explicitly task-owned Git worktrees for isolated coding work."""

import subprocess
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from cubicle import store


def create(engine, home, task_id, repo_path, branch):
    if str(uuid.UUID(task_id)) != task_id:
        raise ValueError("Invalid task ID")
    source = Path(repo_path).expanduser().resolve(strict=True)
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=source,
                          text=True, capture_output=True, check=True, timeout=10).stdout.strip()
    root = Path(root).resolve(strict=True)
    check = subprocess.run(["git", "check-ref-format", "--branch", branch], cwd=root,
                           capture_output=True, check=False, timeout=10)
    if check.returncode or branch.startswith("-"):
        raise ValueError("Invalid branch name")
    target = Path(home).expanduser().resolve() / "worktrees" / task_id
    with Session(engine) as db, db.begin():
        task = db.scalar(select(store.Task).where(store.Task.id == task_id).with_for_update())
        if not task or task.kind != "coding":
            raise ValueError("A coding task is required")
        if task.workspace:
            raise ValueError("Task already has a recorded workspace")
        if target.exists():
            raise ValueError("Task worktree path already exists; inspect it before retrying")
        base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                              text=True, check=True, timeout=10).stdout.strip()
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if target.parent.is_symlink():
            raise ValueError("Worktree directory must not be a symlink")
        subprocess.run(["git", "worktree", "add", "-b", branch, str(target), base], cwd=root,
                       capture_output=True, text=True, check=True, timeout=60)
        task.workspace = {"source": str(root), "path": str(target), "branch": branch, "base": base}
        return task.workspace
