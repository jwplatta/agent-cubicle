"""Host worker launch and durable subprocess output."""

import json
import os
import signal
import subprocess
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from cubicle import store


def create_session(engine, task_id, backend):
    if backend not in {"codex", "claude", "agy"}:
        raise ValueError("Unsupported worker backend")
    with Session(engine) as db, db.begin():
        if not db.get(store.Task, task_id):
            raise ValueError("Task not found")
        session = store.WorkerSession(task_id=task_id, backend=backend)
        db.add(session)
        db.flush()
        return {"id": session.id, "task_id": task_id, "backend": backend}


def start(engine, home, node_id, worker_session_id, cwd):
    path = Path(cwd).expanduser().resolve(strict=True)
    if not path.is_dir():
        raise ValueError("Worker cwd must be a directory")
    with Session(engine) as db, db.begin():
        ws = db.scalar(select(store.WorkerSession).where(
            store.WorkerSession.id == worker_session_id).with_for_update())
        node = db.scalar(select(store.Node).where(store.Node.id == node_id).with_for_update())
        if not ws or not node or node.task_id != ws.task_id:
            raise ValueError("Node and worker session must belong to the same task")
        if node.status not in {"pending", "failed"}:
            raise ValueError("Node is already running, awaiting review, or accepted")
        task = db.get(store.Task, ws.task_id)
        if task.status not in {"ready", "active"}:
            raise ValueError("Task must be ready before dispatch")
        dependencies = list(db.scalars(select(store.Edge.from_id).where(store.Edge.to_id == node_id)))
        for dependency in dependencies:
            if db.get(store.Node, dependency).status != "accepted":
                raise ValueError("Node dependencies are not accepted")
        if db.scalar(select(store.Run.id).where(store.Run.worker_session_id == ws.id,
                                                store.Run.status.in_(["starting", "running", "cancel_requested", "unknown"]))):
            raise ValueError("Worker session already has an active run")
        task.status = "active"
        node.status = "running"
        run = store.Run(node_id=node_id, worker_session_id=ws.id, status="starting",
                        result={"cwd": str(path)})
        db.add(run)
        db.flush()
        run_id = run.id
    run_dir = Path(home) / "runs" / run_id
    try:
        run_dir.mkdir(parents=True, mode=0o700)
        proc = subprocess.Popen([sys.executable, "-m", "cubicle.worker", "run", run_id],
                                start_new_session=True, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                env={**os.environ, "CUBICLE_HOME": str(home)})
    except OSError as exc:
        with Session(engine) as db, db.begin():
            run = db.get(store.Run, run_id)
            run.status = "failed"
            db.get(store.Node, node_id).status = "failed"
            run.result = {"error": str(exc)}
        raise
    return {"run_id": run_id, "pid": proc.pid, "status": "starting"}


def command(backend, prompt, session_id):
    if backend == "codex":
        args = ["codex", "exec", "--json", "--skip-git-repo-check",
                "--dangerously-bypass-approvals-and-sandbox"]
        return args + (["resume", session_id, prompt] if session_id else [prompt])
    if backend == "claude":
        args = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
                "--include-hook-events", "--dangerously-skip-permissions"]
        return args + (["--resume", session_id] if session_id else [])
    if backend == "agy":
        args = ["agy", "-p", prompt, "--output-format", "stream-json",
                "--dangerously-skip-permissions"]
        return args + (["--conversation", session_id] if session_id else [])
    raise ValueError("Unsupported backend")


def run_worker(run_id):
    engine = store.engine_from_env()
    home = Path(os.environ.get("CUBICLE_HOME", Path.home() / ".cubicle"))
    run_dir = home / "runs" / run_id
    try:
        with Session(engine) as db, db.begin():
            run = db.get(store.Run, run_id)
            node = db.get(store.Node, run.node_id)
            ws = db.get(store.WorkerSession, run.worker_session_id)
            cwd = run.result["cwd"]
            prompt = (f"Complete this bounded Cubicle node. Return outputs, checks, decisions and "
                      f"blockers. Do not claim task completion.\nNode: {node.title}\n"
                      f"Objective: {node.objective}\nInputs: {json.dumps(node.inputs)}\n"
                      f"Scope: {json.dumps(node.scope)}\nOutputs: {json.dumps(node.outputs)}\n"
                      f"Checks: {json.dumps(node.checks)}")
            args = command(ws.backend, prompt, ws.provider_session_id)
            run.pid = os.getpid()
            run.result = {**run.result, "process_start": process_start(run.pid)}
            run.status = "running"
        with (run_dir / "stdout.jsonl").open("w") as out, (run_dir / "stderr.log").open("w") as err:
            proc = subprocess.run(args, cwd=cwd, stdout=out, stderr=err,
                                  env={**os.environ, "CUBICLE_RUN_ID": run_id}, check=False)
        terminal = {"exit_code": proc.returncode}
        temp = run_dir / "terminal.tmp"
        temp.write_text(json.dumps(terminal))
        temp.replace(run_dir / "terminal.json")
        reconcile(engine, home, run_id)
    except Exception as exc:
        (run_dir / "worker-error.log").write_text(f"{type(exc).__name__}: {exc}\n")
        raise


def reconcile(engine, home, run_id):
    """Replay completed output idempotently; never infer success from a missing marker."""
    run_dir = Path(home) / "runs" / run_id
    terminal_file = run_dir / "terminal.json"
    if not terminal_file.exists():
        return {"run_id": run_id, "status": "unknown"}
    terminal = json.loads(terminal_file.read_text())
    session_id = None
    rows = []
    completed = False
    for index, line in enumerate((run_dir / "stdout.jsonl").read_text().splitlines()):
        try:
            payload = json.loads(line)
        except ValueError:
            continue
        if not isinstance(payload, dict):
            continue
        result = payload.get("result")
        result = result if isinstance(result, dict) else {}
        session_id = (session_id or payload.get("thread_id") or payload.get("session_id")
                      or payload.get("conversation_id") or result.get("conversation_id"))
        if payload.get("type") == "turn.completed":
            completed = True
        elif payload.get("type") == "result" and not payload.get("is_error", False):
            completed = True
        elif payload.get("event") == "result" and result.get("status") == "SUCCESS":
            completed = True
        rows.append((index, payload))
    hooks = []
    for path in sorted((run_dir / "hooks").glob("*.json")):
        hook = json.loads(path.read_text())
        hooks.append(hook)
    with Session(engine) as db, db.begin():
        run = db.scalar(select(store.Run).where(store.Run.id == run_id).with_for_update())
        if not run:
            raise ValueError("Run not found")
        ws = db.get(store.WorkerSession, run.worker_session_id)
        for index, payload in rows:
            event_id = f"{run_id}:{index}"
            if not db.get(store.Event, event_id):
                db.add(store.Event(id=event_id, run_id=run_id, source="stream",
                                   event_type=payload.get("type") or payload.get("event") or "unknown",
                                   payload=payload))
        for hook in hooks:
            event_id = f"{run_id}:hook:{hook['event_id']}"
            if not db.get(store.Event, event_id):
                db.add(store.Event(id=event_id, run_id=run_id, source="hook",
                                   event_type=hook["event_type"], payload=hook["payload"]))
        if session_id:
            ws.provider_session_id = session_id
        run.status = "succeeded" if terminal["exit_code"] == 0 and completed else "failed"
        node = db.get(store.Node, run.node_id)
        if node.status != "accepted":
            node.status = "awaiting_review" if run.status == "succeeded" else "failed"
        run.result = {**(run.result or {}), **terminal, "session_id": session_id}
        return {"run_id": run_id, "status": run.status, "session_id": session_id}


def process_start(pid):
    """Return the process start identity without exposing its environment."""
    result = subprocess.run(["ps", "-p", str(pid), "-o", "lstart="],
                            capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def cancel(engine, run_id):
    """Request termination only after verifying ownership and process identity."""
    with Session(engine) as db, db.begin():
        run = db.scalar(select(store.Run).where(store.Run.id == run_id).with_for_update())
        if not run or run.status not in {"running", "cancel_requested"} or not run.pid:
            raise ValueError("Run is not a known running worker")
        recorded = (run.result or {}).get("process_start")
        current = process_start(run.pid)
        args = subprocess.run(["ps", "-p", str(run.pid), "-o", "args="],
                              capture_output=True, text=True, check=False)
        if (not recorded or recorded != current or args.returncode != 0
                or f"cubicle.worker run {run_id}" not in args.stdout):
            raise ValueError("Cannot verify worker identity; no signal sent")
        run.status = "cancel_requested"
        pid = run.pid
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        return {"run_id": run_id, "status": "unknown", "detail": "process group disappeared"}
    return {"run_id": run_id, "status": "cancel_requested"}


def get_run(engine, run_id):
    with Session(engine) as db:
        run = db.get(store.Run, run_id)
        if not run:
            raise ValueError("Run not found")
        return {"id": run.id, "node_id": run.node_id, "worker_session_id": run.worker_session_id,
                "status": run.status, "pid": run.pid, "result": run.result}


def read_events(engine, home, run_id, offset=0, limit=50):
    """Read complete JSONL records without consuming a partially written final line."""
    if offset < 0 or not 1 <= limit <= 100:
        raise ValueError("Invalid event cursor or limit")
    get_run(engine, run_id)
    path = Path(home) / "runs" / run_id / "stdout.jsonl"
    if not path.exists():
        return {"events": [], "next_offset": offset}
    events = []
    with path.open("rb") as stream:
        stream.seek(offset)
        while len(events) < limit:
            start = stream.tell()
            line = stream.readline()
            if not line or not line.endswith(b"\n"):
                stream.seek(start)
                break
            try:
                events.append(json.loads(line))
            except (ValueError, UnicodeDecodeError):
                events.append({"type": "invalid_json", "offset": start})
        return {"events": events, "next_offset": stream.tell()}


def accept_node(engine, run_id, evidence):
    if not evidence or not all(isinstance(x, str) and x.strip() for x in evidence):
        raise ValueError("Acceptance requires evidence")
    with Session(engine) as db, db.begin():
        run = db.scalar(select(store.Run).where(store.Run.id == run_id).with_for_update())
        if not run or run.status != "succeeded":
            raise ValueError("Only a successful run can be accepted")
        node = db.get(store.Node, run.node_id)
        if node.status != "awaiting_review":
            raise ValueError("Node is not awaiting review")
        if len(evidence) < len(node.checks):
            raise ValueError("Provide evidence for every check")
        node.status = "accepted"
        run.result = {**(run.result or {}), "acceptance_evidence": evidence}
        return {"node_id": node.id, "status": node.status}


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "run":
        raise SystemExit("Usage: python -m cubicle.worker run RUN_ID")
    run_worker(sys.argv[2])
