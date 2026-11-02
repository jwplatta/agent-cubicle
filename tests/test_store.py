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


def test_version_one_upgrades_without_losing_tasks(tmp_path):
    from sqlalchemy import inspect, text

    engine = create_engine(f"sqlite:///{tmp_path / 'upgrade.db'}")
    with engine.begin() as connection:
        tables = [table for name, table in store.Base.metadata.tables.items()
                  if name not in {"supervisor_events", "graph_changes", "graph_versions"}]
        store.Base.metadata.create_all(connection, tables=tables)
        connection.execute(text("ALTER TABLE tasks DROP COLUMN completion"))
        connection.execute(text("ALTER TABLE tasks DROP COLUMN workspace"))
        connection.execute(text("ALTER TABLE nodes DROP COLUMN current_run_id"))
        connection.execute(text("CREATE TABLE cubicle_schema_version (version INTEGER NOT NULL)"))
        connection.execute(text("INSERT INTO cubicle_schema_version VALUES (1)"))
        connection.execute(text("INSERT INTO tasks (id,title,objective,project,kind,status,acceptance,created_at) VALUES ('old','Keep','Existing','repo','other','draft','[]',CURRENT_TIMESTAMP)"))
    store.initialize_database(engine)
    store.initialize_database(engine)
    assert "supervisor_events" in inspect(engine).get_table_names()
    assert store.list_tasks(engine)[0]["id"] == "old"


def test_review_feedback_reopens_node_and_downstream(engine):
    from sqlalchemy.orm import Session

    task = store.create_task(engine, "Fix", "Repair", "repo", "coding", ["check"])
    a = store.add_node(engine, task["id"], "A", "edit", [], [], ["diff"], ["check"])
    b = store.add_node(engine, task["id"], "B", "test", [], [], ["result"], ["check"])
    store.add_edge(engine, a["id"], b["id"])
    with Session(engine) as db, db.begin():
        db.get(store.Node, a["id"]).status = "accepted"
        db.get(store.Node, b["id"]).status = "accepted"
        db.get(store.Task, task["id"]).status = "awaiting_review"
    result = store.revise_node(engine, a["id"], "Reviewer found an issue")
    assert set(result["affected_nodes"]) == {a["id"], b["id"]}
    graph = store.graph(engine, task["id"])
    assert all(node["status"] == "pending" for node in graph["nodes"])
    assert graph["changes"][0]["reason"] == "Reviewer found an issue"
    assert graph["task"]["status"] == "active"


def test_graph_versions_preserve_previous_topology(engine):
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    task = store.create_task(engine, "T", "O", "P", "other", ["check"])
    a = store.add_node(engine, task["id"], "A", "O", [], [], ["out"], ["check"])
    b = store.add_node(engine, task["id"], "B", "O", [], [], ["out"], ["check"])
    store.add_edge(engine, a["id"], b["id"])
    with Session(engine) as db:
        versions = list(db.scalars(select(store.GraphVersion).order_by(store.GraphVersion.version)))
        assert [v.version for v in versions] == [1, 2, 3, 4]
        assert versions[0].snapshot["nodes"] == []
        assert versions[2].snapshot["edges"] == []
        assert len(versions[3].snapshot["edges"]) == 1
    assert store.graph_version(engine, task["id"], 2)["version"] == 2


def test_review_waits_for_accepted_nodes(engine):
    from sqlalchemy.orm import Session

    task = store.create_task(engine, "T", "O", "P", "other", ["check"])
    node = store.add_node(engine, task["id"], "N", "O", [], [], ["out"], ["check"])
    store.mark_task_ready(engine, task["id"])
    with Session(engine) as db, db.begin():
        db.get(store.Task, task["id"]).status = "active"
    with pytest.raises(ValueError, match="accepted"):
        store.mark_task_awaiting_review(engine, task["id"])
    with Session(engine) as db, db.begin():
        db.get(store.Node, node["id"]).status = "accepted"
    assert store.mark_task_awaiting_review(engine, task["id"])["status"] == "awaiting_review"
