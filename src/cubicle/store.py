"""Database-backed task graphs and execution records."""

import os
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, UniqueConstraint, create_engine, inspect, select, text
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


class Edge(Base):
    __tablename__ = "node_edges"
    __table_args__ = (UniqueConstraint("from_id", "to_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    from_id: Mapped[str] = mapped_column(ForeignKey("nodes.id"))
    to_id: Mapped[str] = mapped_column(ForeignKey("nodes.id"))


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
            if version != 1:
                raise ValueError(f"Unsupported database schema version: {version}")
            return
        if tables.intersection(Base.metadata.tables):
            raise ValueError("Cubicle tables exist without a schema version; refusing to modify them")
        Base.metadata.create_all(connection)
        connection.execute(text("CREATE TABLE cubicle_schema_version (version INTEGER NOT NULL)"))
        connection.execute(text("INSERT INTO cubicle_schema_version (version) VALUES (1)"))


def task_dict(task):
    return {k: getattr(task, k) for k in ("id", "backlog_ref", "title", "objective", "project", "kind", "status", "acceptance")}


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
        return task_dict(task)


def list_tasks(engine):
    with Session(engine) as db:
        return [task_dict(x) for x in db.scalars(select(Task).order_by(Task.created_at))]


def add_node(engine, task_id, title, objective, inputs, scope, outputs, checks):
    if not all([title.strip(), objective.strip(), outputs, checks]):
        raise ValueError("title, objective, outputs and checks are required")
    with Session(engine) as db, db.begin():
        if not db.get(Task, task_id):
            raise ValueError("Task not found")
        node = Node(task_id=task_id, title=title, objective=objective, inputs=inputs,
                    scope=scope, outputs=outputs, checks=checks)
        db.add(node)
        db.flush()
        return {"id": node.id, "task_id": task_id, "title": title, "status": node.status}


def graph(engine, task_id):
    with Session(engine) as db:
        task = db.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")
        nodes = list(db.scalars(select(Node).where(Node.task_id == task_id)))
        ids = [n.id for n in nodes]
        edges = list(db.scalars(select(Edge).where(Edge.from_id.in_(ids)))) if ids else []
        return {"task": task_dict(task), "nodes": [{"id": n.id, "title": n.title,
                "objective": n.objective, "inputs": n.inputs, "scope": n.scope,
                "outputs": n.outputs, "checks": n.checks, "status": n.status} for n in nodes],
                "edges": [{"from": e.from_id, "to": e.to_id} for e in edges]}


def add_edge(engine, from_id, to_id):
    with Session(engine) as db, db.begin():
        a, b = db.get(Node, from_id), db.get(Node, to_id)
        if not a or not b or a.task_id != b.task_id or from_id == to_id:
            raise ValueError("Nodes must be distinct and belong to the same task")
        # Serialize graph edits on the parent row to prevent concurrent cycles.
        db.scalar(select(Task).where(Task.id == a.task_id).with_for_update())
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
