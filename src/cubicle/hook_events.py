"""Spool per-run hook observations independently of the worker process."""

import json
import os
import subprocess
import uuid
from pathlib import Path

from redaction import redact


def spool_if_managed(event_type, payload):
    run_id = os.environ.get("CUBICLE_RUN_ID")
    supervisor_id = os.environ.get("CUBICLE_SUPERVISOR_ID") if not run_id else None
    identity = run_id or supervisor_id
    if not identity:
        return False
    if str(uuid.UUID(identity)) != identity:
        raise ValueError("Invalid Cubicle event identity")
    home = Path(os.environ.get("CUBICLE_HOME", Path.home() / ".cubicle"))
    parent = home / ("runs" if run_id else "supervisors") / identity
    if run_id and not parent.is_dir():
        raise ValueError("Cubicle run directory does not exist")
    directory = parent / "hooks"
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    event_id = str(uuid.uuid4())
    tmp = directory / (event_id + ".tmp")
    final = directory / (event_id + ".json")
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump({"event_id": event_id, "event_type": event_type, "payload": redact(payload)}, stream)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, final)
        if os.environ.get("CUBICLE_PYTHON"):
            subprocess.Popen([os.environ["CUBICLE_PYTHON"], "-m", "cubicle.collector", str(final)],
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
    finally:
        if tmp.exists():
            tmp.unlink()
    return True
