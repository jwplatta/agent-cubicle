"""Database-backed task graphs and execution records."""

import os
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, UniqueConstraint, create_engine, func, inspect, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

JSON_TYPE = JSON().with_variant(JSONB(), "postgresql")


def now():
    return datetime.now(timezone.utc)


def new_id():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    backlog_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(300))
    objective: Mapped[str] = mapped_column(Text)
    project: Mapped[str] = mapped_column(String(300))
    kind: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(30), default="draft")
    acceptance: Mapped[list] = mapped_column(JSON_TYPE, default=list)
    completion: Mapped[dict | None] = mapped_column(JSON_TYPE, nullable=True)
    workspace: Mapped[dict | None] = mapped_column(JSON_TYPE, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Node(Base):
    __tablename__ = "nodes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), index=True)
    title: Mapped[str] = mapped_column(String(300))
    objective: Mapped[str] = mapped_column(Text)
    inputs: Mapped[list] = mapped_column(JSON_TYPE, default=list)
    scope: Mapped[list] = mapped_column(JSON_TYPE, default=list)
    outputs: Mapped[list] = mapped_column(JSON_TYPE, default=list)
    checks: Mapped[list] = mapped_column(JSON_TYPE, default=list)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    current_run_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class Edge(Base):
    __tablename__ = "node_edges"
    __table_args__ = (UniqueConstraint("from_id", "to_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    from_id: Mapped[str] = mapped_column(ForeignKey("nodes.id"))
    to_id: Mapped[str] = mapped_column(ForeignKey("nodes.id"))


class GraphVersion(Base):
    __tablename__ = "graph_versions"
    __table_args__ = (UniqueConstraint("task_id", "version"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), index=True)
    version: Mapped[int] = mapped_column()
    reason: Mapped[str] = mapped_column(Text)
    snapshot: Mapped[dict] = mapped_column(JSON_TYPE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class GraphChange(Base):
    __tablename__ = "graph_changes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), index=True)
    node_id: Mapped[str] = mapped_column(ForeignKey("nodes.id"))
    reason: Mapped[str] = mapped_column(Text)
    affected: Mapped[list] = mapped_column(JSON_TYPE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class WorkerSession(Base):
    __tablename__ = "worker_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), index=True)
    backend: Mapped[str] = mapped_column(String(30))
    provider_session_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="ready")


class Run(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    node_id: Mapped[str] = mapped_column(ForeignKey("nodes.id"), index=True)
    worker_session_id: Mapped[str] = mapped_column(ForeignKey("worker_sessions.id"))
    status: Mapped[str] = mapped_column(String(30), default="starting")
    pid: Mapped[int | None] = mapped_column(nullable=True)
    result: Mapped[dict | None] = mapped_column(JSON_TYPE, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    source: Mapped[str] = mapped_column(String(30))
    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[dict] = mapped_column(JSON_TYPE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class SupervisorEvent(Base):
    __tablename__ = "supervisor_events"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    supervisor_id: Mapped[str] = mapped_column(String(36), index=True)
    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[dict] = mapped_column(JSON_TYPE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


def engine_from_env():
    url = os.environ.get("CUBICLE_DATABASE_URL")
    if not url:
        raise ValueError("Set CUBICLE_DATABASE_URL to the Cubicle PostgreSQL connection URL")
    return create_engine(url, pool_pre_ping=True)


def initialize_database(engine):
    """Apply initial schema once; refuse unknown or unversioned existing tables."""
    with engine.begin() as connection:
        if connection.dialect.name == "postgresql":
            connection.execute(text("SELECT pg_advisory_xact_lock(532604923)"))
        tables = set(inspect(connection).get_table_names())
        if "cubicle_schema_version" in tables:
            version = connection.execute(text("SELECT version FROM cubicle_schema_version")).scalar_one()
            if version == 1:
                SupervisorEvent.__table__.create(connection, checkfirst=False)
                version = 2
                connection.execute(text("UPDATE cubicle_schema_version SET version = 2"))
            if version == 2:
                connection.execute(text("ALTER TABLE tasks ADD COLUMN completion JSONB"))
                version = 3
                connection.execute(text("UPDATE cubicle_schema_version SET version = 3"))
            if version == 3:
                GraphChange.__table__.create(connection, checkfirst=False)
                version = 4
                connection.execute(text("UPDATE cubicle_schema_version SET version = 4"))
            if version == 4:
                connection.execute(text("ALTER TABLE nodes ADD COLUMN current_run_id VARCHAR(36)"))
                connection.execute(text("UPDATE nodes SET current_run_id = (SELECT id FROM runs WHERE runs.node_id = nodes.id ORDER BY created_at DESC, id DESC LIMIT 1)"))
                version = 5
                connection.execute(text("UPDATE cubicle_schema_version SET version = 5"))
            if version == 5:
                GraphVersion.__table__.create(connection, checkfirst=False)
                version = 6
                connection.execute(text("UPDATE cubicle_schema_version SET version = 6"))
            if version == 6:
                connection.execute(text("ALTER TABLE tasks ADD COLUMN workspace JSONB"))
                version = 7
                connection.execute(text("UPDATE cubicle_schema_version SET version = 7"))
            if version != 7:
                raise ValueError(f"Unsupported database schema version: {version}")
            return
        if tables.intersection(Base.metadata.tables):
            raise ValueError("Cubicle tables exist without a schema version; refusing to modify them")
        Base.metadata.create_all(connection)
        connection.execute(text("CREATE TABLE cubicle_schema_version (version INTEGER NOT NULL)"))
        connection.execute(text("INSERT INTO cubicle_schema_version (version) VALUES (7)"))


def task_dict(task):
    return {k: getattr(task, k) for k in ("id", "backlog_ref", "title", "objective", "project", "kind", "status", "acceptance", "completion", "workspace")}


def snapshot_graph(db, task_id, reason):
    """Persist a graph snapshot while the caller holds the task row lock."""
    db.flush()
    nodes = list(db.scalars(select(Node).where(Node.task_id == task_id)))
    ids = [n.id for n in nodes]
    edges = list(db.scalars(select(Edge).where(Edge.from_id.in_(ids)))) if ids else []
    version = (db.scalar(select(func.max(GraphVersion.version)).where(
        GraphVersion.task_id == task_id)) or 0) + 1
    snapshot = {"nodes": [{"id": n.id, "title": n.title, "objective": n.objective,
                "inputs": n.inputs, "scope": n.scope, "outputs": n.outputs,
                "checks": n.checks, "status": n.status} for n in nodes],
                "edges": [{"from": e.from_id, "to": e.to_id} for e in edges]}
    db.add(GraphVersion(task_id=task_id, version=version, reason=reason, snapshot=snapshot))


def create_task(engine, title, objective, project, kind, acceptance, backlog_ref=None):
    if kind not in {"coding", "other"}:
        raise ValueError("kind must be coding or other")
    if not all([title.strip(), objective.strip(), project.strip(), acceptance]):
        raise ValueError("title, objective, project and acceptance checks are required")
    with Session(engine) as db, db.begin():
        task = Task(title=title, objective=objective, project=project, kind=kind,
                    acceptance=acceptance, backlog_ref=backlog_ref)
        db.add(task)
        db.flush()
        snapshot_graph(db, task.id, "Task created")
        return task_dict(task)


def list_tasks(engine):
    with Session(engine) as db:
        return [task_dict(x) for x in db.scalars(select(Task).order_by(Task.created_at))]


def add_node(engine, task_id, title, objective, inputs, scope, outputs, checks):
    if not all([title.strip(), objective.strip(), outputs, checks]):
        raise ValueError("title, objective, outputs and checks are required")
    with Session(engine) as db, db.begin():
        task = db.scalar(select(Task).where(Task.id == task_id).with_for_update())
        if not task:
            raise ValueError("Task not found")
        if task.status == "completed":
            raise ValueError("Completed tasks cannot be changed")
        node = Node(task_id=task_id, title=title, objective=objective, inputs=inputs,
                    scope=scope, outputs=outputs, checks=checks)
        db.add(node)
        db.flush()
        snapshot_graph(db, task_id, "Node added")
        return {"id": node.id, "task_id": task_id, "title": title, "status": node.status}


def graph(engine, task_id):
    with Session(engine) as db:
        task = db.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")
        nodes = list(db.scalars(select(Node).where(Node.task_id == task_id)))
        ids = [n.id for n in nodes]
        edges = list(db.scalars(select(Edge).where(Edge.from_id.in_(ids)))) if ids else []
        versions = list(db.scalars(select(GraphVersion).where(GraphVersion.task_id == task_id)
                                   .order_by(GraphVersion.version)))
        changes = list(db.scalars(select(GraphChange).where(GraphChange.task_id == task_id)
                                  .order_by(GraphChange.created_at)))
        return {"task": task_dict(task), "versions": [{"id": v.id, "version": v.version,
                "reason": v.reason} for v in versions], "changes": [{"id": c.id, "node_id": c.node_id,
                "reason": c.reason, "affected_nodes": c.affected} for c in changes], "nodes": [{"id": n.id, "title": n.title,
                "objective": n.objective, "inputs": n.inputs, "scope": n.scope,
                "outputs": n.outputs, "checks": n.checks, "status": n.status,
                "current_run_id": n.current_run_id} for n in nodes],
                "edges": [{"from": e.from_id, "to": e.to_id} for e in edges]}


def add_edge(engine, from_id, to_id):
    with Session(engine) as db, db.begin():
        a, b = db.get(Node, from_id), db.get(Node, to_id)
        if not a or not b or a.task_id != b.task_id or from_id == to_id:
            raise ValueError("Nodes must be distinct and belong to the same task")
        # Serialize graph edits on the parent row to prevent concurrent cycles.
        task = db.scalar(select(Task).where(Task.id == a.task_id).with_for_update())
        if task.status == "completed":
            raise ValueError("Completed tasks cannot be changed")
        ids = list(db.scalars(select(Node.id).where(Node.task_id == a.task_id)))
        edges = list(db.scalars(select(Edge).where(Edge.from_id.in_(ids))))
        pending = [to_id]
        seen = set()
        while pending:
            item = pending.pop()
            if item == from_id:
                raise ValueError("Dependency would create a cycle")
            if item not in seen:
                seen.add(item)
                pending.extend(e.to_id for e in edges if e.from_id == item)
        db.add(Edge(from_id=from_id, to_id=to_id))
        snapshot_graph(db, task.id, "Dependency added")
        return {"from": from_id, "to": to_id}


def mark_task_ready(engine, task_id):
    with Session(engine) as db, db.begin():
        task = db.scalar(select(Task).where(Task.id == task_id).with_for_update())
        if not task:
            raise ValueError("Task not found")
        if task.status != "draft":
            raise ValueError("Only draft tasks can be marked ready")
        task.status = "ready"
        return task_dict(task)


def revise_node(engine, node_id, reason):
    if not reason.strip():
        raise ValueError("A reason is required")
    with Session(engine) as db, db.begin():
        node = db.get(Node, node_id)
        if not node:
            raise ValueError("Node not found")
        task = db.scalar(select(Task).where(Task.id == node.task_id).with_for_update())
        if task.status == "completed":
            raise ValueError("Completed tasks cannot be changed")
        nodes = list(db.scalars(select(Node).where(Node.task_id == task.id).with_for_update()))
        ids = [n.id for n in nodes]
        edges = list(db.scalars(select(Edge).where(Edge.from_id.in_(ids))))
        affected = set()
        pending = [node_id]
        while pending:
            current = pending.pop()
            if current not in affected:
                affected.add(current)
                pending.extend(edge.to_id for edge in edges if edge.from_id == current)
        if any(n.status == "running" for n in nodes if n.id in affected):
            raise ValueError("Cannot revise while an affected node is running")
        for item in nodes:
            if item.id in affected:
                item.status = "pending"
                item.current_run_id = None
        if task.status == "awaiting_review":
            task.status = "active"
        change = GraphChange(task_id=task.id, node_id=node_id, reason=reason, affected=sorted(affected))
        db.add(change)
        db.flush()
        snapshot_graph(db, task.id, reason)
        return {"change_id": change.id, "affected_nodes": sorted(affected),
                "task_id": task.id, "backlog_ref": task.backlog_ref}


def mark_task_awaiting_review(engine, task_id):
    with Session(engine) as db, db.begin():
        task = db.scalar(select(Task).where(Task.id == task_id).with_for_update())
        if not task or task.status != "active":
            raise ValueError("Only an active task can be sent for review")
        nodes = list(db.scalars(select(Node).where(Node.task_id == task_id)))
        if not nodes or any(node.status != "accepted" for node in nodes):
            raise ValueError("Every node must be accepted before task review")
        task.status = "awaiting_review"
        return task_dict(task)


def graph_version(engine, task_id, version):
    with Session(engine) as db:
        record = db.scalar(select(GraphVersion).where(
            GraphVersion.task_id == task_id, GraphVersion.version == version))
        if not record:
            raise ValueError("Graph version not found")
        return {"id": record.id, "task_id": task_id, "version": version,
                "reason": record.reason, "snapshot": record.snapshot}
