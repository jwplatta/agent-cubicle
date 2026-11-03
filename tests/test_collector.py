import json
import uuid
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from cubicle import collector, store


def test_supervisor_hook_collection_is_idempotent(monkeypatch, tmp_path):
    url = f"sqlite:///{tmp_path / 'state.db'}"
    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path))
    monkeypatch.setenv("CUBICLE_DATABASE_URL", url)
    monkeypatch.setenv("SYNTHETIC_API_KEY", "synthetic-collector-secret-xyz")
    engine = create_engine(url)
    store.initialize_database(engine)
    supervisor_id, event_id = str(uuid.uuid4()), str(uuid.uuid4())
    directory = tmp_path / "supervisors" / supervisor_id / "hooks"
    directory.mkdir(parents=True)
    path = directory / (event_id + ".json")
    path.write_text(json.dumps({"event_id": event_id, "event_type": "session_start", "payload": {
        "message": "synthetic-collector-secret-xyz"}}))
    collector.collect(path)
    collector.collect(path)
    with Session(engine) as db:
        rows = list(db.scalars(select(store.SupervisorEvent)))
        assert len(rows) == 1
        assert rows[0].supervisor_id == supervisor_id
        assert rows[0].payload["message"] == "[REDACTED]"


def test_worker_hook_collection_and_replay_are_idempotent(monkeypatch, tmp_path):
    url = f"sqlite:///{tmp_path / 'state.db'}"
    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path))
    monkeypatch.setenv("CUBICLE_DATABASE_URL", url)
    engine = create_engine(url)
    store.initialize_database(engine)
    task = store.create_task(engine, "Test", "Test collection", "test", "other", ["done"])
    node = store.add_node(engine, task["id"], "Node", "Check", [], [], ["result"], ["check"])
    with Session(engine) as db, db.begin():
        session = store.WorkerSession(task_id=task["id"], backend="codex")
        db.add(session)
        db.flush()
        run = store.Run(node_id=node["id"], worker_session_id=session.id, status="running")
        db.add(run)
        db.flush()
        run_id = run.id
    event_id = str(uuid.uuid4())
    directory = tmp_path / "runs" / run_id / "hooks"
    directory.mkdir(parents=True)
    path = directory / (event_id + ".json")
    path.write_text(json.dumps({"event_id": event_id, "event_type": "tool", "payload": {}}))
    collector.collect(path)
    assert collector.collect_pending(tmp_path) == 0
    with Session(engine) as db:
        rows = list(db.scalars(select(store.Event)))
        assert len(rows) == 1
        assert rows[0].run_id == run_id
