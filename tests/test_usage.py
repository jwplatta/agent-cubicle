import time

import pytest
from sqlalchemy import create_engine

from cubicle import quota_statusline, store, usage, worker


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
