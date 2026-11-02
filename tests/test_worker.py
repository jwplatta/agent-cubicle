import json
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from cubicle import store, worker


def test_completed_worker_spool_can_be_replayed(monkeypatch, tmp_path):
    url = f"sqlite:///{tmp_path / 'worker.db'}"
    monkeypatch.setenv("CUBICLE_DATABASE_URL", url)
    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path))
    engine = create_engine(url)
    store.initialize_database(engine)
    task = store.create_task(engine, "Fix", "Fix it", "repo", "coding", ["tests"])
    store.mark_task_ready(engine, task["id"])
    node = store.add_node(engine, task["id"], "Investigate", "Find cause", [], [], ["report"], ["exists"])
    session = worker.create_session(engine, task["id"], "codex")
    with Session(engine) as db, db.begin():
        db.get(store.Node, node["id"]).status = "running"
        run = store.Run(node_id=node["id"], worker_session_id=session["id"], result={"cwd": str(tmp_path)})
        db.add(run)
        db.flush()
        run_id = run.id
        db.get(store.Node, node["id"]).current_run_id = run_id
    (tmp_path / "runs" / run_id).mkdir(parents=True)

    def fake_run(args, cwd, stdout, stderr, env, check):
        assert env["CUBICLE_RUN_ID"] == run_id
        stdout.write(json.dumps({"type": "thread.started", "thread_id": "provider-1"}) + "\n")
        stdout.write(json.dumps({"type": "turn.completed", "usage": {"input_tokens": 5}}) + "\n")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(worker.subprocess, "run", fake_run)
    monkeypatch.setattr(worker, "process_start", lambda pid: "test-start")
    worker.run_worker(run_id)
    assert worker.reconcile(engine, tmp_path, run_id)["status"] == "succeeded"
    with Session(engine) as db:
        assert len(list(db.scalars(select(store.Event)))) == 2
        assert db.get(store.WorkerSession, session["id"]).provider_session_id == "provider-1"
    assert worker.accept_node(engine, run_id, ["report exists"])["status"] == "accepted"


def test_missing_terminal_is_unknown(engine=None, tmp_path=None):
    # Tested without a database because reconciliation must not guess from missing output.
    assert worker.reconcile(None, "/nonexistent-cubicle-probe", "missing")["status"] == "unknown"


def test_worker_command_resumes_each_backend():
    for backend in ("codex", "claude", "agy"):
        assert "session-1" in worker.command(backend, "prompt", "session-1")
    with pytest.raises(ValueError):
        worker.command("unknown", "prompt", None)


def test_two_node_assignments_resume_same_provider_session(monkeypatch, tmp_path):
    import os
    import time

    url = f"sqlite:///{tmp_path / 'integration.db'}"
    monkeypatch.setenv("CUBICLE_DATABASE_URL", url)
    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path))
    fake = tmp_path / "codex"
    fake.write_text('#!/bin/sh\nprintf \'%s\\n\' \'{"type":"thread.started","thread_id":"same-thread"}\' \'{"type":"turn.completed"}\'\n')
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    engine = create_engine(url)
    store.initialize_database(engine)
    task = store.create_task(engine, "Fix", "Fix it", "repo", "coding", ["checks"])
    store.mark_task_ready(engine, task["id"])
    first = store.add_node(engine, task["id"], "First", "One", [], [], ["a"], ["a"])
    second = store.add_node(engine, task["id"], "Second", "Two", [], [], ["b"], ["b"])
    store.add_edge(engine, first["id"], second["id"])
    session = worker.create_session(engine, task["id"], "codex")
    with pytest.raises(ValueError, match="dependencies"):
        worker.start(engine, tmp_path, second["id"], session["id"], str(tmp_path))

    def run_node(node):
        run = worker.start(engine, tmp_path, node["id"], session["id"], str(tmp_path))
        end = time.monotonic() + 10
        while time.monotonic() < end:
            state = worker.get_run(engine, run["run_id"])
            if state["status"] in {"succeeded", "failed"}:
                return state
            time.sleep(.05)
        raise AssertionError("worker did not finish")

    one = run_node(first)
    assert one["status"] == "succeeded"
    worker.accept_node(engine, one["id"], ["first checked"])
    two = run_node(second)
    assert two["status"] == "succeeded"
    with Session(engine) as db:
        assert db.get(store.WorkerSession, session["id"]).provider_session_id == "same-thread"
        assert len(list(db.scalars(select(store.Event)))) == 4


def test_stream_cursor_does_not_consume_partial_record(monkeypatch, tmp_path):
    url = f"sqlite:///{tmp_path / 'stream.db'}"
    engine = create_engine(url)
    store.initialize_database(engine)
    task = store.create_task(engine, "T", "O", "P", "other", ["check"])
    node = store.add_node(engine, task["id"], "N", "O", [], [], ["out"], ["check"])
    sess = worker.create_session(engine, task["id"], "codex")
    with Session(engine) as db, db.begin():
        run = store.Run(node_id=node["id"], worker_session_id=sess["id"])
        db.add(run)
        db.flush()
        run_id = run.id
    path = tmp_path / "runs" / run_id / "stdout.jsonl"
    path.parent.mkdir(parents=True)
    path.write_bytes(b'{"type":"one"}\n{"type":')
    first = worker.read_events(engine, tmp_path, run_id)
    assert first["events"] == [{"type": "one"}]
    with path.open("ab") as f:
        f.write(b'"two"}\n')
    second = worker.read_events(engine, tmp_path, run_id, first["next_offset"])
    assert second["events"] == [{"type": "two"}]


def test_cancel_only_signals_verified_worker_process_group(monkeypatch, tmp_path):
    import os
    import time

    url = f"sqlite:///{tmp_path / 'cancel.db'}"
    monkeypatch.setenv("CUBICLE_DATABASE_URL", url)
    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path))
    fake = tmp_path / "codex"
    fake.write_text('#!/bin/sh\nsleep 30\n')
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    engine = create_engine(url)
    store.initialize_database(engine)
    task = store.create_task(engine, "T", "O", "P", "other", ["check"])
    store.mark_task_ready(engine, task["id"])
    node = store.add_node(engine, task["id"], "N", "O", [], [], ["out"], ["check"])
    sess = worker.create_session(engine, task["id"], "codex")
    launched = worker.start(engine, tmp_path, node["id"], sess["id"], str(tmp_path))
    cancelled = False
    try:
        end = time.monotonic() + 10
        while time.monotonic() < end:
            state = worker.get_run(engine, launched["run_id"])
            if state["status"] == "running":
                break
            time.sleep(.05)
        assert state["status"] == "running"
        assert worker.cancel(engine, launched["run_id"])["status"] == "cancel_requested"
        cancelled = True
        assert worker.reconcile(engine, tmp_path, launched["run_id"])["status"] == "unknown"
    finally:
        if not cancelled:
            try:
                os.killpg(launched["pid"], 15)
            except ProcessLookupError:
                pass


def test_two_workstreams_run_concurrently(monkeypatch, tmp_path):
    import os
    import time

    url = f"sqlite:///{tmp_path / 'parallel.db'}"
    monkeypatch.setenv("CUBICLE_DATABASE_URL", url)
    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path))
    fake = tmp_path / "codex"
    fake.write_text('#!/bin/sh\nprintf \'%s\\n\' \'{"type":"thread.started","thread_id":"thread"}\'\nsleep 1\nprintf \'%s\\n\' \'{"type":"turn.completed"}\'\n')
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    engine = create_engine(url)
    store.initialize_database(engine)
    runs = []
    for project in ("repo-a", "repo-b"):
        task = store.create_task(engine, project, "Fix", project, "coding", ["check"])
        store.mark_task_ready(engine, task["id"])
        node = store.add_node(engine, task["id"], "Node", "Inspect", [], [], ["out"], ["check"])
        sess = worker.create_session(engine, task["id"], "codex")
        runs.append(worker.start(engine, tmp_path, node["id"], sess["id"], str(tmp_path)))
    assert runs[0]["run_id"] != runs[1]["run_id"]
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        states = [worker.get_run(engine, run["run_id"])["status"] for run in runs]
        if states == ["succeeded", "succeeded"]:
            break
        time.sleep(.05)
    assert states == ["succeeded", "succeeded"]


def test_terminal_spool_recovers_after_database_ingestion_failure(monkeypatch, tmp_path):
    url = f"sqlite:///{tmp_path / 'recovery.db'}"
    monkeypatch.setenv("CUBICLE_DATABASE_URL", url)
    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path))
    engine = create_engine(url)
    store.initialize_database(engine)
    task = store.create_task(engine, "T", "O", "P", "other", ["check"])
    node = store.add_node(engine, task["id"], "N", "O", [], [], ["out"], ["check"])
    sess = worker.create_session(engine, task["id"], "codex")
    with Session(engine) as db, db.begin():
        run = store.Run(node_id=node["id"], worker_session_id=sess["id"], result={"cwd": str(tmp_path)})
        db.add(run)
        db.flush()
        run_id = run.id
    (tmp_path / "runs" / run_id).mkdir(parents=True)

    def fake_run(args, cwd, stdout, stderr, env, check):
        stdout.write('{"type":"thread.started","thread_id":"saved"}\n')
        stdout.write('{"type":"turn.completed"}\n')
        return SimpleNamespace(returncode=0)

    original = worker.reconcile
    monkeypatch.setattr(worker.subprocess, "run", fake_run)
    monkeypatch.setattr(worker, "process_start", lambda pid: "start")
    monkeypatch.setattr(worker, "reconcile", lambda *args: (_ for _ in ()).throw(RuntimeError("db down")))
    with pytest.raises(RuntimeError, match="db down"):
        worker.run_worker(run_id)
    assert (tmp_path / "runs" / run_id / "terminal.json").exists()
    assert (tmp_path / "runs" / run_id / "worker-error.log").exists()
    monkeypatch.setattr(worker, "reconcile", original)
    assert original(engine, tmp_path, run_id)["status"] == "succeeded"
    assert original(engine, tmp_path, run_id)["status"] == "succeeded"
    with Session(engine) as db:
        assert len(list(db.scalars(select(store.Event)))) == 2


def test_cancel_refuses_unverified_process(monkeypatch, tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'identity.db'}")
    store.initialize_database(engine)
    task = store.create_task(engine, "T", "O", "P", "other", ["check"])
    node = store.add_node(engine, task["id"], "N", "O", [], [], ["out"], ["check"])
    sess = worker.create_session(engine, task["id"], "codex")
    with Session(engine) as db, db.begin():
        run = store.Run(node_id=node["id"], worker_session_id=sess["id"], status="running",
                        pid=1234, result={"process_start": "old-start"})
        db.add(run)
        db.flush()
        run_id = run.id
    signals = []
    monkeypatch.setattr(worker, "process_start", lambda pid: "different-start")
    monkeypatch.setattr(worker.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout=""))
    monkeypatch.setattr(worker.os, "killpg", lambda *args: signals.append(args))
    with pytest.raises(ValueError, match="Cannot verify"):
        worker.cancel(engine, run_id)
    assert not signals


def test_reconcile_ingests_late_hook_once(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'hooks.db'}")
    store.initialize_database(engine)
    task = store.create_task(engine, "T", "O", "P", "other", ["check"])
    node = store.add_node(engine, task["id"], "N", "O", [], [], ["out"], ["check"])
    sess = worker.create_session(engine, task["id"], "codex")
    with Session(engine) as db, db.begin():
        run = store.Run(node_id=node["id"], worker_session_id=sess["id"])
        db.add(run)
        db.flush()
        run_id = run.id
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "hooks").mkdir(parents=True)
    (run_dir / "stdout.jsonl").write_text('{"type":"turn.completed"}\n')
    (run_dir / "terminal.json").write_text('{"exit_code":0}')
    worker.reconcile(engine, tmp_path, run_id)
    (run_dir / "hooks" / "late.json").write_text(json.dumps({"event_id": "late", "event_type": "pre_tool_use", "payload": {"tool": "Bash"}}))
    worker.reconcile(engine, tmp_path, run_id)
    worker.reconcile(engine, tmp_path, run_id)
    with Session(engine) as db:
        rows = list(db.scalars(select(store.Event)))
        assert len(rows) == 2
        assert sum(row.source == "hook" for row in rows) == 1


def test_cancel_requested_session_cannot_start_another_node(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'blocked.db'}")
    store.initialize_database(engine)
    task = store.create_task(engine, "T", "O", "P", "other", ["check"])
    store.mark_task_ready(engine, task["id"])
    a = store.add_node(engine, task["id"], "A", "O", [], [], ["out"], ["check"])
    b = store.add_node(engine, task["id"], "B", "O", [], [], ["out"], ["check"])
    sess = worker.create_session(engine, task["id"], "codex")
    with Session(engine) as db, db.begin():
        db.add(store.Run(node_id=a["id"], worker_session_id=sess["id"], status="cancel_requested"))
    with pytest.raises(ValueError, match="active run"):
        worker.start(engine, tmp_path, b["id"], sess["id"], str(tmp_path))


def test_recover_confirms_cancelled_only_when_group_is_gone(monkeypatch, tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'recover-cancel.db'}")
    store.initialize_database(engine)
    task = store.create_task(engine, "T", "O", "P", "other", ["check"])
    node = store.add_node(engine, task["id"], "N", "O", [], [], ["out"], ["check"])
    sess = worker.create_session(engine, task["id"], "codex")
    with Session(engine) as db, db.begin():
        run = store.Run(node_id=node["id"], worker_session_id=sess["id"],
                        status="cancel_requested", pid=1234, result={"process_start": "old"})
        db.add(run)
        db.flush()
        run_id = run.id
    monkeypatch.setattr(worker, "process_start", lambda pid: None)
    def no_group(pid, sig):
        raise ProcessLookupError()
    monkeypatch.setattr(worker.os, "killpg", no_group)
    assert worker.recover(engine, tmp_path, run_id)["status"] == "cancelled"
    with Session(engine) as db:
        assert db.get(store.Node, node["id"]).status == "failed"


def test_startup_recovery_isolated_per_run(monkeypatch, tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'recovery-scan.db'}")
    store.initialize_database(engine)
    task = store.create_task(engine, "Recovery", "Recover pending", "test", "other", ["done"])
    node = store.add_node(engine, task["id"], "Node", "Check", [], [], ["result"], ["check"])
    with Session(engine) as db, db.begin():
        session = store.WorkerSession(task_id=task["id"], backend="codex")
        db.add(session)
        db.flush()
        runs = [store.Run(node_id=node["id"], worker_session_id=session.id, status="running")
                for _ in range(2)]
        db.add_all(runs)
        db.flush()
        ids = [run.id for run in runs]
    def recover_one(engine, home, run_id):
        if run_id == ids[0]:
            raise OSError("unavailable")
        return {"run_id": run_id, "status": "unknown"}
    monkeypatch.setattr(worker, "recover", recover_one)
    results = worker.recover_pending(engine, tmp_path)
    assert {result["status"] for result in results} == {"unknown", "recovery_error"}


def test_replaying_old_run_does_not_undo_graph_revision(monkeypatch, tmp_path):
    url = f"sqlite:///{tmp_path / 'revision.db'}"
    monkeypatch.setenv("CUBICLE_DATABASE_URL", url)
    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path))
    engine = create_engine(url)
    store.initialize_database(engine)
    task = store.create_task(engine, "T", "O", "P", "other", ["check"])
    node = store.add_node(engine, task["id"], "N", "O", [], [], ["out"], ["check"])
    sess = worker.create_session(engine, task["id"], "codex")
    with Session(engine) as db, db.begin():
        db.get(store.Node, node["id"]).status = "accepted"
        run = store.Run(node_id=node["id"], worker_session_id=sess["id"], status="succeeded")
        db.add(run)
        db.flush()
        run_id = run.id
    directory = tmp_path / "runs" / run_id
    directory.mkdir(parents=True)
    (directory / "stdout.jsonl").write_text('{"type":"turn.completed"}\n')
    (directory / "terminal.json").write_text('{"exit_code":0}')
    store.revise_node(engine, node["id"], "Review feedback")
    worker.reconcile(engine, tmp_path, run_id)
    assert store.graph(engine, task["id"])["nodes"][0]["status"] == "pending"


def test_replaying_old_run_does_not_complete_active_retry(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'retry.db'}")
    store.initialize_database(engine)
    task = store.create_task(engine, "T", "O", "P", "other", ["check"])
    node = store.add_node(engine, task["id"], "N", "O", [], [], ["out"], ["check"])
    sess = worker.create_session(engine, task["id"], "codex")
    with Session(engine) as db, db.begin():
        db.get(store.Node, node["id"]).status = "running"
        old = store.Run(node_id=node["id"], worker_session_id=sess["id"], status="succeeded")
        current = store.Run(node_id=node["id"], worker_session_id=sess["id"], status="running")
        db.add_all([old, current])
        db.flush()
        old_id = old.id
    directory = tmp_path / "runs" / old_id
    directory.mkdir(parents=True)
    (directory / "stdout.jsonl").write_text('{"type":"turn.completed"}\n')
    (directory / "terminal.json").write_text('{"exit_code":0}')
    worker.reconcile(engine, tmp_path, old_id)
    assert store.graph(engine, task["id"])["nodes"][0]["status"] == "running"
