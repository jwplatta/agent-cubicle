"""A shared Markdown backlog with stable IDs."""

import fcntl
import os
import tempfile
import uuid
from datetime import date
from pathlib import Path

import yaml


def backlog_dir():
    return Path(os.environ.get("CUBICLE_HOME", Path.home() / ".cubicle")) / "backlog"


def create(title, description, project, kind="feature", tags=None):
    if not all(x.strip() for x in (title, description, project)):
        raise ValueError("title, description and project are required")
    if kind not in {"feature", "bug", "chore", "documentation"}:
        raise ValueError("invalid backlog type")
    root = backlog_dir()
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    identifier = str(uuid.uuid4())
    item = {"id": identifier, "type": kind, "title": title, "description": description,
            "project": project, "tags": tags or [], "status": "not-started",
            "priority": "medium", "source": "cubicle/supervisor",
            "created": str(date.today()), "updated": str(date.today())}
    path = root / f"{identifier}.md"
    content = "---\n" + yaml.safe_dump(item, sort_keys=False) + "---\n\n## Summary\n\n" + description + "\n"
    with path.open("x", encoding="utf-8") as f:
        f.write(content)
    return {**item, "path": str(path)}


def list_items():
    root = backlog_dir()
    result = []
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) != 3 or parts[0].strip():
            continue
        item = yaml.safe_load(parts[1])
        if isinstance(item, dict):
            result.append({**item, "path": str(path)})
    return result


def update(item_id, status=None, priority=None, body=None, *, allow_complete=False):
    try:
        identifier = str(uuid.UUID(item_id))
    except ValueError as exc:
        raise ValueError("Invalid backlog ID") from exc
    if status is not None and status not in {"not-started", "ready", "in-progress", "awaiting-review", "blocked", "complete"}:
        raise ValueError("Invalid status")
    if priority is not None and priority not in {"low", "medium", "high", "critical"}:
        raise ValueError("Invalid priority")
    if status == "complete" and not allow_complete:
        raise ValueError("Completion requires the task-specific completion workflow")
    root = backlog_dir()
    path = root / f"{identifier}.md"
    lock = root / ".backlog.lock"
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    with lock.open("a") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) != 3 or parts[0].strip():
            raise ValueError("Backlog item has invalid frontmatter")
        item = yaml.safe_load(parts[1])
        if not isinstance(item, dict) or item.get("id") != identifier:
            raise ValueError("Backlog item ID does not match its filename")
        if status is not None:
            item["status"] = status
        if priority is not None:
            item["priority"] = priority
        item["updated"] = str(date.today())
        content = "---\n" + yaml.safe_dump(item, sort_keys=False) + "---" + ("\n" + body if body is not None else parts[2])
        fd, tmp = tempfile.mkstemp(dir=root, prefix=".backlog-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    return {**item, "path": str(path)}
