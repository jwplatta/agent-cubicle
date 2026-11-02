import time

import pytest
from sqlalchemy import create_engine

from cubicle import quota_statusline, store, usage, worker


@pytest.mark.parametrize("used,allowed", [(40, True), (80, False), (95, False)])
def test_codex_usage_threshold(monkeypatch, tmp_path, used, allowed):
    monkeypatch.setattr(usage, "codex_limits", lambda: {
        "rateLimitsByLimitId": {"codex": {"primary": {"usedPercent": used}}}})
    if allowed:
        assert usage.check_codex(tmp_path)["max_used_percent"] == used
    else:
        with pytest.raises(ValueError, match="limit reached"):
            usage.check_codex(tmp_path)


def test_codex_unavailable_pauses_dispatch(monkeypatch, tmp_path):
    monkeypatch.setattr(usage, "codex_limits", lambda: {})
    with pytest.raises(ValueError, match="usage unavailable"):
        usage.check_codex(tmp_path)


def test_codex_dispatch_stops_before_mutating_task_when_over_limit(monkeypatch, tmp_path):
    monkeypatch.setattr(usage, "codex_limits", lambda: {
        "rateLimits": {"primary": {"usedPercent": 90}}})
    engine = create_engine(f"sqlite:///{tmp_path / 'state.db'}")
    store.initialize_database(engine)
    task = store.create_task(engine, "Quota", "Check quota", "test", "other", ["done"])
    node = store.add_node(engine, task["id"], "Node", "Check", [], [], ["result"], ["check"])
    store.mark_task_ready(engine, task["id"])
    session = worker.create_session(engine, task["id"], "codex")
    with pytest.raises(ValueError, match="limit reached"):
        worker.start(engine, tmp_path, node["id"], session["id"], tmp_path)
    assert store.graph(engine, task["id"])["nodes"][0]["status"] == "pending"


def test_supervisor_poll_reports_quota_threshold(monkeypatch, tmp_path):
    from sqlalchemy.orm import Session
    from cubicle import mcp_server

    monkeypatch.setattr(usage, "codex_limits", lambda: {
        "rateLimits": {"primary": {"usedPercent": 90}}})
    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path))
    engine = create_engine(f"sqlite:///{tmp_path / 'state.db'}")
    store.initialize_database(engine)
    task = store.create_task(engine, "Quota", "Check quota", "test", "other", ["done"])
    node = store.add_node(engine, task["id"], "Node", "Check", [], [], ["result"], ["check"])
    with Session(engine) as db, db.begin():
        session = store.WorkerSession(task_id=task["id"], backend="codex")
        db.add(session)
        db.flush()
        run = store.Run(node_id=node["id"], worker_session_id=session.id, status="running")
        db.add(run)
        db.flush()
        run_id = run.id
    monkeypatch.setattr(mcp_server, "get_engine", lambda: engine)
    assert mcp_server.get_run(run_id)["usage_review_due"] is True


def test_agy_quota_blocks_stale_missing_or_exhausted_and_allows_available(tmp_path):
    with pytest.raises(ValueError, match="unavailable or stale"):
        usage.check_agy(tmp_path)
    assert quota_statusline.record(tmp_path, {"quota": {"weekly": {"remaining_fraction": 0.5}}})
    usage.check_agy(tmp_path)
    assert quota_statusline.record(tmp_path, {"quota": {"weekly": {"remaining_fraction": 0.1}}})
    with pytest.raises(ValueError, match="limit reached"):
        usage.check_agy(tmp_path)
    path = tmp_path / "usage" / "agy.json"
    path.write_text('{"observed_at": %s, "remaining_fractions": {"weekly": 0.5}}' % (time.time() - 301))
    with pytest.raises(ValueError, match="unavailable or stale"):
        usage.check_agy(tmp_path)


def test_statusline_never_stores_other_payload_fields(tmp_path):
    assert quota_statusline.record(tmp_path, {"secret": "synthetic-secret", "quota": {
        "model": {"remaining_fraction": 0.9}}})
    assert "synthetic-secret" not in (tmp_path / "usage" / "agy.json").read_text()


def test_agy_dispatch_does_not_start_without_a_fresh_quota(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'state.db'}")
    store.initialize_database(engine)
    task = store.create_task(engine, "Quota", "Check quota", "test", "other", ["done"])
    node = store.add_node(engine, task["id"], "Node", "Check", [], [], ["result"], ["check"])
    store.mark_task_ready(engine, task["id"])
    session = worker.create_session(engine, task["id"], "agy")
    with pytest.raises(ValueError, match="unavailable or stale"):
        worker.start(engine, tmp_path, node["id"], session["id"], tmp_path)
    assert store.graph(engine, task["id"])["nodes"][0]["status"] == "pending"
