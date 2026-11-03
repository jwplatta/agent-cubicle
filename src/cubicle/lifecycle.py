"""Evidence-based task completion; merging is always a separate action."""

import json
import os
import subprocess
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from cubicle import backlog, store


def _ready_for_completion(db, task_id, kind):
    task = db.scalar(select(store.Task).where(store.Task.id == task_id).with_for_update())
    if not task or task.kind != kind:
        raise ValueError(f"Task not found or not {kind}")
    nodes = list(db.scalars(select(store.Node).where(store.Node.task_id == task_id)))
    if not nodes or any(node.status != "accepted" for node in nodes):
        raise ValueError("Every graph node must be accepted before completion")
    return task


def _sync_backlog(task):
    if not task["backlog_ref"]:
        return task
    try:
        backlog.update(task["backlog_ref"], status="complete", allow_complete=True)
    except (OSError, ValueError) as exc:
        task["backlog_sync_error"] = str(exc)
    return task


def complete_other(engine, task_id, confirmation):
    if not confirmation.strip():
        raise ValueError("Explicit user confirmation is required")
    with Session(engine) as db, db.begin():
        task = _ready_for_completion(db, task_id, "other")
        task.status = "completed"
        task.completion = {"user_confirmation": confirmation}
        result = store.task_dict(task)
    return _sync_backlog(result)


def _verified_merged_pr(engine, task_id, repo_path, pr_number):
    if not isinstance(pr_number, int) or pr_number < 1:
        raise ValueError("Pull request number must be a positive integer")
    root = Path(repo_path).expanduser().resolve(strict=True)
    with Session(engine) as db:
        task = db.get(store.Task, task_id)
        if not task or task.kind != "coding":
            raise ValueError("Coding task not found")
        workspace = task.workspace
        node_ids = list(db.scalars(select(store.Node.id).where(store.Node.task_id == task_id)))
        runs = list(db.scalars(select(store.Run).where(store.Run.node_id.in_(node_ids)))) if node_ids else []
        run_paths = [(run.result or {}).get("cwd") for run in runs]
        run_ids = [run.id for run in runs]
        events = list(db.scalars(select(store.Event).where(store.Event.run_id.in_(run_ids)))) if run_ids else []
        payloads = [json.dumps(event.payload) for event in events]
    if workspace:
        if Path(workspace["source"]).resolve() != root:
            raise ValueError("Repository must match the task's source repository")
        if not any(path and Path(path).resolve() == Path(workspace["path"]).resolve()
                   for path in run_paths):
            raise ValueError("No worker run belongs to the task worktree")
    elif not any(path and Path(path).resolve() == root for path in run_paths):
        raise ValueError("Repository must match a recorded worker directory")
    pr = subprocess.run(["gh", "pr", "view", str(pr_number), "--json", "state,headRefName,url"],
                        cwd=root, capture_output=True, text=True, check=True, timeout=30)
    info = json.loads(pr.stdout)
    if info.get("state") != "MERGED":
        raise ValueError("Pull request has not been merged")
    pr_url = info.get("url")
    if not isinstance(pr_url, str) or not pr_url:
        raise ValueError("Pull request URL is unavailable")
    if not any(pr_url in payload for payload in payloads):
        raise ValueError("Pull request is not linked to recorded task output")
    branch = info.get("headRefName")
    if not isinstance(branch, str) or not branch:
        raise ValueError("Pull request branch is unavailable")
    if workspace and workspace.get("branch") != branch:
        raise ValueError("Pull request branch does not match the task worktree")
    return root, info, branch, workspace


def cleanup_merged_branch(engine, task_id, repo_path, pr_number):
    root, info, branch, workspace = _verified_merged_pr(engine, task_id, repo_path, pr_number)
    if workspace:
        home = Path(os.environ.get("CUBICLE_HOME", Path.home() / ".cubicle")).expanduser().resolve()
        expected = home / "worktrees" / task_id
        target = Path(workspace["path"])
        if target != expected or target.is_symlink() or target.parent.is_symlink():
            raise ValueError("Task worktree path is not a verified Cubicle worktree")
        if target.exists():
            top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=target,
                                 capture_output=True, text=True, check=True, timeout=10).stdout.strip()
            current = subprocess.run(["git", "branch", "--show-current"], cwd=target,
                                     capture_output=True, text=True, check=True, timeout=10).stdout.strip()
            source_common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root,
                                           capture_output=True, text=True, check=True, timeout=10).stdout.strip()
            target_common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=target,
                                           capture_output=True, text=True, check=True, timeout=10).stdout.strip()
            if (Path(top).resolve() != target.resolve() or current != branch or
                    (root / source_common).resolve() != (target / target_common).resolve()):
                raise ValueError("Task worktree identity does not match the recorded repository")
            status = subprocess.run(["git", "status", "--porcelain", "--ignored", "--untracked-files=all"],
                                    cwd=target, capture_output=True, text=True, check=True, timeout=30)
            if status.stdout.strip():
                raise ValueError("Task worktree contains uncommitted, untracked, or ignored files")
            subprocess.run(["git", "worktree", "remove", str(target)], cwd=root,
                           capture_output=True, text=True, check=True, timeout=30)
    exists = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
                            cwd=root, check=False, timeout=10)
    if exists.returncode == 1:
        return {"branch": branch, "status": "already_absent", "pull_request": info["url"]}
    if exists.returncode != 0:
        raise ValueError("Could not verify local task branch")
    # Git refuses to delete a checked-out branch or one not merged into local HEAD.
    deleted = subprocess.run(["git", "branch", "-d", "--", branch], cwd=root,
                             capture_output=True, text=True, check=False, timeout=10)
    if deleted.returncode:
        raise ValueError("Git refused safe local branch deletion; manual review is required")
    return {"branch": branch, "status": "deleted", "pull_request": info["url"]}


def complete_coding(engine, task_id, repo_path, pr_number):
    root, info, branch, workspace = _verified_merged_pr(engine, task_id, repo_path, pr_number)
    if workspace and Path(workspace["path"]).exists():
        raise ValueError("Task worktree still exists")
    result = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
                            cwd=root, check=False, timeout=10)
    if result.returncode == 0:
        raise ValueError("Local task branch still exists")
    if result.returncode != 1:
        raise ValueError("Could not verify local task branch")
    with Session(engine) as db, db.begin():
        task = _ready_for_completion(db, task_id, "coding")
        task.status = "completed"
        task.completion = {"pull_request": info["url"], "branch": branch,
                           "repository": str(root), "merged": True, "local_branch_removed": True}
        result = store.task_dict(task)
    return _sync_backlog(result)
