import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from cubicle import lifecycle, store


def setup_task(tmp_path, kind):
    engine = create_engine(f"sqlite:///{tmp_path / 'lifecycle.db'}")
    store.initialize_database(engine)
    task = store.create_task(engine, "Task", "Objective", "project", kind, ["checks"])
    node = store.add_node(engine, task["id"], "Node", "Objective", [], [], ["out"], ["check"])
    return engine, task, node


def test_noncoding_completion_requires_confirmation_and_accepted_nodes(tmp_path):
    engine, task, node = setup_task(tmp_path, "other")
    with pytest.raises(ValueError, match="confirmation"):
        lifecycle.complete_other(engine, task["id"], "")
    with pytest.raises(ValueError, match="accepted"):
        lifecycle.complete_other(engine, task["id"], "User confirmed")
    with Session(engine) as db, db.begin():
        db.get(store.Node, node["id"]).status = "accepted"
    assert lifecycle.complete_other(engine, task["id"], "User confirmed")["status"] == "completed"


def test_coding_completion_requires_merged_pr_linked_to_task_and_no_branch(monkeypatch, tmp_path):
    engine, task, node = setup_task(tmp_path, "coding")
    with Session(engine) as db, db.begin():
        db.get(store.Node, node["id"]).status = "accepted"
        session = store.WorkerSession(task_id=task["id"], backend="codex")
        db.add(session)
        db.flush()
        run = store.Run(node_id=node["id"], worker_session_id=session.id,
                        status="succeeded", result={"cwd": str(tmp_path)})
        db.add(run)
        db.flush()
        db.add(store.Event(id="one", run_id=run.id, source="stream", event_type="result",
                           payload={"text": "https://github.com/example/repo/pull/1"}))
    responses = iter([
        SimpleNamespace(stdout=json.dumps({"state": "OPEN", "headRefName": "branch", "url": "https://github.com/example/repo/pull/1"})),
        SimpleNamespace(stdout=json.dumps({"state": "MERGED", "headRefName": "branch", "url": "https://github.com/example/repo/pull/1"})),
        SimpleNamespace(returncode=0),
        SimpleNamespace(stdout=json.dumps({"state": "MERGED", "headRefName": "branch", "url": "https://github.com/example/repo/pull/1"})),
        SimpleNamespace(returncode=1),
    ])
    monkeypatch.setattr(lifecycle.subprocess, "run", lambda *a, **k: next(responses))
    with pytest.raises(ValueError, match="not been merged"):
        lifecycle.complete_coding(engine, task["id"], tmp_path, 1)
    with pytest.raises(ValueError, match="branch still exists"):
        lifecycle.complete_coding(engine, task["id"], tmp_path, 1)
    assert lifecycle.complete_coding(engine, task["id"], tmp_path, 1)["status"] == "completed"


def test_noncoding_completion_updates_linked_backlog(monkeypatch, tmp_path):
    from cubicle import backlog

    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path))
    item = backlog.create("Task", "Details", "repo")
    engine = create_engine(f"sqlite:///{tmp_path / 'linked.db'}")
    store.initialize_database(engine)
    task = store.create_task(engine, "Task", "Objective", "repo", "other", ["checks"], item["id"])
    node = store.add_node(engine, task["id"], "Node", "Objective", [], [], ["out"], ["check"])
    with Session(engine) as db, db.begin():
        db.get(store.Node, node["id"]).status = "accepted"
    result = lifecycle.complete_other(engine, task["id"], "The user confirmed completion")
    assert result["status"] == "completed"
    assert backlog.list_items()[0]["status"] == "complete"


def test_safe_cleanup_and_completion_after_merge(monkeypatch, tmp_path):
    import subprocess

    repo = tmp_path / "repo"
    repo.mkdir()
    def git(*args):
        return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)
    git("init", "-b", "main")
    git("config", "user.email", "cubicle-test@example.invalid")
    git("config", "user.name", "Cubicle Test")
    (repo / "file").write_text("base")
    git("add", "file")
    git("commit", "-m", "base")
    git("switch", "-c", "feature")
    (repo / "file").write_text("merged")
    git("commit", "-am", "change")
    git("switch", "main")
    git("merge", "--ff-only", "feature")
    engine, task, node = setup_task(tmp_path, "coding")
    url = "https://github.com/example/repo/pull/1"
    with Session(engine) as db, db.begin():
        db.get(store.Node, node["id"]).status = "accepted"
        ws = store.WorkerSession(task_id=task["id"], backend="codex")
        db.add(ws)
        db.flush()
        run = store.Run(node_id=node["id"], worker_session_id=ws.id,
                        status="succeeded", result={"cwd": str(repo)})
        db.add(run)
        db.flush()
        db.add(store.Event(id="pr", run_id=run.id, source="stream", event_type="result",
                           payload={"text": url}))
    real_run = subprocess.run
    def fake_gh(args, **kwargs):
        if args[0] == "gh":
            return SimpleNamespace(stdout=json.dumps({"state": "MERGED", "headRefName": "feature", "url": url}))
        return real_run(args, **kwargs)
    monkeypatch.setattr(lifecycle.subprocess, "run", fake_gh)
    assert lifecycle.cleanup_merged_branch(engine, task["id"], repo, 1)["status"] == "deleted"
    assert lifecycle.complete_coding(engine, task["id"], repo, 1)["status"] == "completed"


def test_task_owned_worktree_cleanup_preserves_dirty_files(monkeypatch, tmp_path):
    import subprocess
    from cubicle import workspaces

    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path / "cubicle"))
    repo = tmp_path / "source"
    repo.mkdir()
    def git(cwd, *args):
        return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "cubicle-test@example.invalid")
    git(repo, "config", "user.name", "Cubicle Test")
    (repo / "file").write_text("base")
    git(repo, "add", "file")
    git(repo, "commit", "-m", "base")
    engine, task, node = setup_task(tmp_path, "coding")
    workspace = workspaces.create(engine, tmp_path / "cubicle", task["id"], repo, "task-branch")
    worktree = Path(workspace["path"])
    (worktree / "file").write_text("merged")
    git(worktree, "commit", "-am", "change")
    git(repo, "merge", "--ff-only", "task-branch")
    url = "https://github.com/example/repo/pull/2"
    with Session(engine) as db, db.begin():
        db.get(store.Node, node["id"]).status = "accepted"
        ws = store.WorkerSession(task_id=task["id"], backend="codex")
        db.add(ws)
        db.flush()
        run = store.Run(node_id=node["id"], worker_session_id=ws.id,
                        status="succeeded", result={"cwd": str(worktree)})
        db.add(run)
        db.flush()
        db.add(store.Event(id="worktree-pr", run_id=run.id, source="stream",
                           event_type="result", payload={"text": url}))
    real_run = subprocess.run
    def fake_gh(args, **kwargs):
        if args[0] == "gh":
            return SimpleNamespace(stdout=json.dumps({"state": "MERGED", "headRefName": "task-branch", "url": url}))
        return real_run(args, **kwargs)
    monkeypatch.setattr(lifecycle.subprocess, "run", fake_gh)
    (worktree / "untracked").write_text("keep")
    with pytest.raises(ValueError, match="untracked"):
        lifecycle.cleanup_merged_branch(engine, task["id"], repo, 2)
    assert (worktree / "untracked").read_text() == "keep"
    (worktree / "untracked").unlink()
    assert lifecycle.cleanup_merged_branch(engine, task["id"], repo, 2)["status"] == "deleted"
    assert not worktree.exists()
    assert lifecycle.complete_coding(engine, task["id"], repo, 2)["status"] == "completed"
