"""Spool per-run hook observations independently of the worker process."""

import json
import os
import uuid
from pathlib import Path


def spool_if_managed(event_type, payload):
    run_id = os.environ.get("CUBICLE_RUN_ID")
    if not run_id:
        return False
    # Do not permit paths to be supplied through an untrusted environment value.
    if str(uuid.UUID(run_id)) != run_id:
        raise ValueError("Invalid Cubicle run ID")
    home = Path(os.environ.get("CUBICLE_HOME", Path.home() / ".cubicle"))
    run_dir = home / "runs" / run_id
    if not run_dir.is_dir():
        raise ValueError("Cubicle run directory does not exist")
    directory = run_dir / "hooks"
    directory.mkdir(exist_ok=True, mode=0o700)
    event_id = str(uuid.uuid4())
    tmp = directory / (event_id + ".tmp")
    final = directory / (event_id + ".json")
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump({"event_id": event_id, "event_type": event_type, "payload": payload}, stream)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, final)
    finally:
        if tmp.exists():
            tmp.unlink()
    return True
