"""Local MCP interface for Cubicle task graphs."""

import os

from mcp.server.fastmcp import FastMCP

from cubicle import backlog, store, worker

mcp = FastMCP("Cubicle", host=os.environ.get("CUBICLE_MCP_HOST", "127.0.0.1"),
              port=int(os.environ.get("CUBICLE_MCP_PORT", "8765")))
_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = store.engine_from_env()
    return _engine


@mcp.tool()
def create_backlog_item(title: str, description: str, project: str,
                        kind: str = "feature", tags: list[str] | None = None) -> dict:
    """Create a shared Markdown backlog item with a stable ID."""
    return backlog.create(title, description, project, kind, tags)


@mcp.tool()
def list_backlog_items() -> list[dict]:
    """List shared Markdown backlog items."""
    return backlog.list_items()


@mcp.tool()
def update_backlog_item(item_id: str, status: str | None = None,
                        priority: str | None = None, body: str | None = None) -> dict:
    """Update a backlog item without changing its ID; completion is handled separately."""
    return backlog.update(item_id, status, priority, body)


@mcp.tool()
def create_task(title: str, objective: str, project: str, kind: str,
                acceptance: list[str], backlog_ref: str | None = None) -> dict:
    """Create a draft task; kind is coding or other."""
    return store.create_task(get_engine(), title, objective, project, kind, acceptance, backlog_ref)


@mcp.tool()
def list_tasks() -> list[dict]:
    """List Cubicle tasks and their statuses."""
    return store.list_tasks(get_engine())


@mcp.tool()
def mark_task_ready(task_id: str) -> dict:
    """Mark a sufficiently specified draft task ready; does not start work."""
    return store.mark_task_ready(get_engine(), task_id)


@mcp.tool()
def add_node(task_id: str, title: str, objective: str, inputs: list[str],
             scope: list[str], outputs: list[str], checks: list[str]) -> dict:
    """Define a bounded node for a task."""
    return store.add_node(get_engine(), task_id, title, objective, inputs, scope, outputs, checks)


@mcp.tool()
def add_dependency(from_id: str, to_id: str) -> dict:
    """Add a dependency between nodes in the same task, rejecting cycles."""
    return store.add_edge(get_engine(), from_id, to_id)


@mcp.tool()
def show_graph(task_id: str) -> dict:
    """Show a task's nodes and dependency edges."""
    return store.graph(get_engine(), task_id)


@mcp.tool()
def create_worker_session(task_id: str, backend: str) -> dict:
    """Create a reusable worker session for a task."""
    return worker.create_session(get_engine(), task_id, backend)


@mcp.tool()
def start_node(node_id: str, worker_session_id: str, cwd: str) -> dict:
    """Start a node on the host; requires local worker execution to be enabled."""
    if os.environ.get("CUBICLE_ENABLE_WORKERS") != "1":
        raise ValueError("Host worker execution is disabled for this MCP server")
    home = os.environ.get("CUBICLE_HOME", os.path.expanduser("~/.cubicle"))
    return worker.start(get_engine(), home, node_id, worker_session_id, cwd)


@mcp.tool()
def reconcile_run(run_id: str) -> dict:
    """Recover terminal output or conservatively inspect an incomplete run."""
    home = os.environ.get("CUBICLE_HOME", os.path.expanduser("~/.cubicle"))
    return worker.recover(get_engine(), home, run_id)


@mcp.tool()
def get_run(run_id: str) -> dict:
    """Get a worker run's status and result metadata."""
    return worker.get_run(get_engine(), run_id)


@mcp.tool()
def cancel_run(run_id: str) -> dict:
    """Request cancellation of a verified local worker process group."""
    if os.environ.get("CUBICLE_ENABLE_WORKERS") != "1":
        raise ValueError("Host worker execution is disabled for this MCP server")
    return worker.cancel(get_engine(), run_id)


@mcp.tool()
def get_run_events(run_id: str, offset: int = 0, limit: int = 50) -> dict:
    """Read complete streamed output records for a run, including while it is active."""
    home = os.environ.get("CUBICLE_HOME", os.path.expanduser("~/.cubicle"))
    return worker.read_events(get_engine(), home, run_id, offset, limit)


@mcp.tool()
def accept_node(run_id: str, evidence: list[str]) -> dict:
    """Accept a successful node after inspecting its check evidence."""
    return worker.accept_node(get_engine(), run_id, evidence)


def main():
    mcp.run(transport=os.environ.get("CUBICLE_MCP_TRANSPORT", "stdio"))


if __name__ == "__main__":
    main()
