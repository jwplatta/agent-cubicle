import pytest
from sqlalchemy import create_engine

from cubicle import backlog, store


@pytest.fixture
def engine(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    store.initialize_database(engine)
    return engine


def test_graph_rejects_cycles_and_cross_task_dependencies(engine):
    a = store.create_task(engine, "Task", "Fix", "repo-a", "coding", ["tests"])
    b = store.create_task(engine, "Other", "Research", "repo-b", "other", ["report"])
    def node(task, name):
        return store.add_node(engine, task, name, "objective", [], [], ["output"], ["check"])
    first, second, other = node(a["id"], "first"), node(a["id"], "second"), node(b["id"], "other")
    store.add_edge(engine, first["id"], second["id"])
    with pytest.raises(ValueError, match="cycle"):
        store.add_edge(engine, second["id"], first["id"])
    with pytest.raises(ValueError, match="same task"):
        store.add_edge(engine, first["id"], other["id"])
    assert len(store.graph(engine, a["id"])["edges"]) == 1
    store.initialize_database(engine)


def test_backlog_items_have_stable_id_and_remain_files(monkeypatch, tmp_path):
    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path))
    item = backlog.create("Research", "Inspect source", "repo", tags=["research"])
    assert backlog.list_items()[0]["id"] == item["id"]
    assert (tmp_path / "backlog" / f"{item['id']}.md").is_file()


def test_task_readiness_is_explicit(engine):
    task = store.create_task(engine, "Plan", "Investigate", "repo", "other", ["report"])
    assert store.mark_task_ready(engine, task["id"])["status"] == "ready"
    with pytest.raises(ValueError, match="draft"):
        store.mark_task_ready(engine, task["id"])


def test_backlog_update_preserves_body_and_rejects_unverified_completion(monkeypatch, tmp_path):
    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path))
    item = backlog.create("Task", "Detailed summary", "repo")
    backlog.update(item["id"], status="ready", priority="high")
    assert "Detailed summary" in (tmp_path / "backlog" / f"{item['id']}.md").read_text()
    assert backlog.list_items()[0]["status"] == "ready"
    with pytest.raises(ValueError, match="Completion"):
        backlog.update(item["id"], status="complete")


def test_backlog_replacing_body_retains_valid_frontmatter(monkeypatch, tmp_path):
    monkeypatch.setenv("CUBICLE_HOME", str(tmp_path))
    item = backlog.create("Task", "Details", "repo")
    backlog.update(item["id"], body="\n## Requirements\n\n- Verify result\n")
    assert backlog.list_items()[0]["id"] == item["id"]


def test_initialization_refuses_unversioned_tables(tmp_path):
    from sqlalchemy import text

    engine = create_engine(f"sqlite:///{tmp_path / 'existing.db'}")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE tasks (id TEXT PRIMARY KEY)"))
    with pytest.raises(ValueError, match="without a schema version"):
        store.initialize_database(engine)
