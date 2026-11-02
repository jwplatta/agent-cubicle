"""Host worker launch and durable subprocess output."""

import hashlib
import json
import os
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from cubicle import backlog, bootstrap, store, usage


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


def start(engine, home, node_id, worker_session_id, cwd, model=None, max_turns=None):
    path = Path(cwd).expanduser().resolve(strict=True)
    if not path.is_dir():
        raise ValueError("Worker cwd must be a directory")
    if model is not None and (not isinstance(model, str) or not model.strip()):
        raise ValueError("Model must be a nonempty string")
    if max_turns is not None and (isinstance(max_turns, bool) or
                                  not isinstance(max_turns, int) or max_turns < 1):
        raise ValueError("max_turns must be a positive integer")
    with Session(engine) as db, db.begin():
        initial = db.get(store.WorkerSession, worker_session_id)
        if not initial:
            raise ValueError("Worker session not found")
        task = db.scalar(select(store.Task).where(store.Task.id == initial.task_id).with_for_update())
        ws = db.scalar(select(store.WorkerSession).where(
            store.WorkerSession.id == worker_session_id).with_for_update())
        node = db.scalar(select(store.Node).where(store.Node.id == node_id).with_for_update())
        if not ws or not node or node.task_id != ws.task_id:
            raise ValueError("Node and worker session must belong to the same task")
        if ws.backend == "claude" and max_turns is None:
            config_path = Path(home) / "config.yaml"
            config = yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
            max_turns = (config or {}).get("limits", {}).get("claude_max_turns", 30)
            if isinstance(max_turns, bool) or not isinstance(max_turns, int) or max_turns < 1:
                raise ValueError("limits.claude_max_turns must be a positive integer")
        if max_turns is not None and ws.backend != "claude":
            raise ValueError("max_turns is currently supported only for Claude workers")
        if ws.backend == "agy":
            usage.check_agy(home)
        elif ws.backend == "codex":
            usage.check_codex(home)
        if node.status not in {"pending", "failed"}:
            raise ValueError("Node is already running, awaiting review, or accepted")
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
        backlog_ref = task.backlog_ref
        node.status = "running"
        run = store.Run(node_id=node_id, worker_session_id=ws.id, status="starting",
                        result={"cwd": str(path), "model": model, "max_turns": max_turns})
        db.add(run)
        db.flush()
        run_id = run.id
        node.current_run_id = run_id
    run_dir = Path(home) / "runs" / run_id
    try:
        bootstrap.initialize(Path(home))
        run_dir.mkdir(parents=True, mode=0o700)
        proc = subprocess.Popen([sys.executable, "-m", "cubicle.worker", "run", run_id],
                                start_new_session=True, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                env={**os.environ, "CUBICLE_HOME": str(home)})
    except (OSError, ValueError) as exc:
        with Session(engine) as db, db.begin():
            run = db.get(store.Run, run_id)
            run.status = "failed"
            db.get(store.Node, node_id).status = "failed"
            run.result = {"error": str(exc)}
        raise
    result = {"run_id": run_id, "pid": proc.pid, "status": "starting"}
    if backlog_ref:
        try:
            backlog.update(backlog_ref, status="in-progress")
        except (OSError, ValueError) as exc:
            result["backlog_sync_error"] = str(exc)
    return result


def command(backend, prompt, session_id, model=None, max_turns=None):
    if backend == "codex":
        args = ["codex", "exec", "--json", "--skip-git-repo-check",
                "--dangerously-bypass-approvals-and-sandbox"]
        if model:
            args += ["--model", model]
        return args + (["resume", session_id, prompt] if session_id else [prompt])
    if backend == "claude":
        args = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
                "--include-hook-events", "--dangerously-skip-permissions"]
        if model:
            args += ["--model", model]
        if max_turns is not None:
            args += ["--max-turns", str(max_turns)]
        return args + (["--resume", session_id] if session_id else [])
    if backend == "agy":
        args = ["agy", "-p", prompt, "--output-format", "stream-json",
                "--dangerously-skip-permissions"]
        if model:
            args += ["--model", model]
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
            task = db.get(store.Task, ws.task_id)
            changes = list(db.scalars(select(store.GraphChange).where(
                store.GraphChange.task_id == task.id).order_by(store.GraphChange.created_at.desc())))
            feedback = next((change.reason for change in changes if node.id in change.affected), None)
            skill = bootstrap.skill_path(home, "cubicle-worker")
            prompt = (f"Read and follow the Cubicle worker skill at {skill}. "
                      f"Complete this bounded Cubicle node. Return outputs, checks, decisions and "
                      f"blockers. Do not claim task completion.\nTask: {task.title}\n"
                      f"Task objective: {task.objective}\nTask acceptance: {json.dumps(task.acceptance)}\n"
                      f"Latest relevant review feedback: {feedback or 'none'}\nNode: {node.title}\n"
                      f"Objective: {node.objective}\nInputs: {json.dumps(node.inputs)}\n"
                      f"Scope: {json.dumps(node.scope)}\nOutputs: {json.dumps(node.outputs)}\n"
                      f"Checks: {json.dumps(node.checks)}")
            args = command(ws.backend, prompt, ws.provider_session_id,
                           run.result.get("model"), run.result.get("max_turns"))
            run.pid = os.getpid()
            manifest = {"task_id": task.id, "node_id": node.id, "backend": ws.backend,
                        "provider_session_id": ws.provider_session_id, "cwd": cwd,
                        "model": run.result.get("model"), "max_turns": run.result.get("max_turns"),
                        "skill_path": str(skill), "skill_sha256": skill.parent.name,
                        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
            run.result = {**run.result, "process_start": process_start(run.pid),
                          "context_manifest": manifest, "prompt": prompt}
            run.status = "running"
        with (run_dir / "stdout.jsonl").open("w") as out, (run_dir / "stderr.log").open("w") as err:
            proc = subprocess.run(args, cwd=cwd, stdout=out, stderr=err,
                                  env={**os.environ, "CUBICLE_RUN_ID": run_id,
                                       "CUBICLE_PYTHON": sys.executable}, check=False)
        terminal = {"exit_code": proc.returncode, "finished_at": datetime.now(timezone.utc).isoformat()}
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
        initial = db.get(store.Run, run_id)
        if not initial:
            raise ValueError("Run not found")
        initial_node = db.get(store.Node, initial.node_id)
        db.scalar(select(store.Task).where(store.Task.id == initial_node.task_id).with_for_update())
        run = db.scalar(select(store.Run).where(store.Run.id == run_id).with_for_update())
        ws = db.get(store.WorkerSession, run.worker_session_id)
        for index, payload in rows:
            event_id = f"{run_id}:{index}"
            if not db.get(store.Event, event_id):
                db.add(store.Event(id=event_id, run_id=run_id, source="stream",
                                   event_type=payload.get("type") or payload.get("event") or "unknown",
                                   payload=payload))
        for hook in hooks:
            event_id = f"{run_id}:hook:{hook['event_id']}"
            insert = pg_insert if engine.dialect.name == "postgresql" else sqlite_insert
            db.execute(insert(store.Event).values(
                id=event_id, run_id=run_id, source="hook", event_type=hook["event_type"],
                payload=hook["payload"]).on_conflict_do_nothing(index_elements=["id"]))
        if session_id:
            if ws.provider_session_id and ws.provider_session_id != session_id:
                raise ValueError("Provider session changed; a new worker session is required")
            ws.provider_session_id = session_id
        run.status = "succeeded" if terminal["exit_code"] == 0 and completed else "failed"
        node = db.get(store.Node, run.node_id)
        other_active = db.scalar(select(store.Run.id).where(
            store.Run.node_id == node.id, store.Run.id != run_id,
            store.Run.status.in_(["starting", "running", "cancel_requested", "unknown"])))
        if node.status == "running" and node.current_run_id == run_id and not other_active:
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
                or f"cubicle.worker run {run_id}" not in args.stdout
                or os.getpgid(run.pid) != run.pid):
            raise ValueError("Cannot verify worker identity; no signal sent")
        run.status = "cancel_requested"
        pid = run.pid
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        return {"run_id": run_id, "status": "unknown", "detail": "process group disappeared"}
    return {"run_id": run_id, "status": "cancel_requested"}


def recover(engine, home, run_id):
    """Reconcile terminal output or conservatively inspect a nonterminal worker."""
    terminal = Path(home) / "runs" / run_id / "terminal.json"
    if terminal.exists():
        return reconcile(engine, home, run_id)
    with Session(engine) as db, db.begin():
        run = db.scalar(select(store.Run).where(store.Run.id == run_id).with_for_update())
        if not run:
            raise ValueError("Run not found")
        if run.status not in {"starting", "running", "cancel_requested", "unknown"}:
            return {"run_id": run_id, "status": run.status}
        if not run.pid:
            return {"run_id": run_id, "status": "unknown", "detail": "launch identity unavailable"}
        current = process_start(run.pid)
        recorded = (run.result or {}).get("process_start")
        if current and current == recorded:
            return {"run_id": run_id, "status": run.status, "detail": "worker process exists"}
        if current:
            return {"run_id": run_id, "status": "unknown", "detail": "PID identity changed"}
        if run.status == "cancel_requested":
            try:
                os.killpg(run.pid, 0)
            except ProcessLookupError:
                run.status = "cancelled"
                db.get(store.Node, run.node_id).status = "failed"
                return {"run_id": run_id, "status": "cancelled"}
            except PermissionError:
                pass
        run.status = "unknown"
        return {"run_id": run_id, "status": "unknown", "detail": "no terminal evidence"}


def recover_pending(engine, home):
    """Reconcile interrupted runs without relaunching work or assuming success."""
    with Session(engine) as db:
        ids = list(db.scalars(select(store.Run.id).where(
            store.Run.status.in_(["starting", "running", "cancel_requested", "unknown"]))))
    results = []
    for run_id in ids:
        try:
            results.append(recover(engine, home, run_id))
        except Exception as exc:
            print(f"Worker recovery failed for {run_id}: {type(exc).__name__}", file=sys.stderr)
            results.append({"run_id": run_id, "status": "recovery_error"})
    return results


def get_run(engine, run_id):
    with Session(engine) as db:
        run = db.get(store.Run, run_id)
        if not run:
            raise ValueError("Run not found")
        session = db.get(store.WorkerSession, run.worker_session_id)
        created = run.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        finished_at = (run.result or {}).get("finished_at")
        end = (datetime.fromisoformat(finished_at) if finished_at else
               datetime.now(timezone.utc) if run.status in {
                   "starting", "running", "cancel_requested", "unknown"} else None)
        return {"id": run.id, "node_id": run.node_id, "worker_session_id": run.worker_session_id,
                "status": run.status, "pid": run.pid, "result": run.result,
                "backend": session.backend,
                "created_at": created.isoformat(),
                "elapsed_seconds": max(0, (end - created).total_seconds()) if end else None}


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
        initial = db.get(store.Run, run_id)
        if not initial:
            raise ValueError("Run not found")
        initial_node = db.get(store.Node, initial.node_id)
        db.scalar(select(store.Task).where(store.Task.id == initial_node.task_id).with_for_update())
        run = db.scalar(select(store.Run).where(store.Run.id == run_id).with_for_update())
        if not run or run.status != "succeeded":
            raise ValueError("Only a successful run can be accepted")
        node = db.get(store.Node, run.node_id)
        if node.status != "awaiting_review" or node.current_run_id != run_id:
            raise ValueError("Node is not awaiting review for this run")
        if len(evidence) < len(node.checks):
            raise ValueError("Provide evidence for every check")
        node.status = "accepted"
        run.result = {**(run.result or {}), "acceptance_evidence": evidence}
        return {"node_id": node.id, "status": node.status}


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "run":
        raise SystemExit("Usage: python -m cubicle.worker run RUN_ID")
    run_worker(sys.argv[2])
