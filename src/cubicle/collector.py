"""Idempotently ingest supervisor hook events from the local spool."""

import json
import os
import sys
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from cubicle import store


def collect(path):
    path = Path(path)
    home = Path(os.environ.get("CUBICLE_HOME", Path.home() / ".cubicle")).resolve()
    path = path.resolve()
    if path.parent.name != "hooks" or path.suffix != ".json":
        raise ValueError("Invalid supervisor event path")
    owner = path.parent.parent
    if owner.parent not in (home / "supervisors", home / "runs"):
        raise ValueError("Invalid event owner")
    identity = owner.name
    record = json.loads(path.read_text())
    for key, value in dotenv_values(home / ".env").items():
        if value is not None:
            os.environ.setdefault(key, value)
    engine = store.engine_from_env()
    insert = {"postgresql": pg_insert, "sqlite": sqlite_insert}.get(engine.dialect.name)
    if insert is None:
        raise ValueError("Unsupported database dialect")
    if owner.parent.name == "supervisors":
        statement = insert(store.SupervisorEvent).values(
            id=record["event_id"], supervisor_id=identity,
            event_type=record["event_type"], payload=record["payload"])
    else:
        statement = insert(store.Event).values(
            id=f"{identity}:hook:{record['event_id']}", run_id=identity, source="hook",
            event_type=record["event_type"], payload=record["payload"])
    statement = statement.on_conflict_do_nothing(index_elements=["id"])
    with engine.begin() as connection:
        connection.execute(statement)



def collect_pending(home):
    """Retry supervisor spool files after a previous collector failure."""
    failures = 0
    paths = (path for root in ("supervisors", "runs")
             for path in (Path(home) / root).glob("*/hooks/*.json"))
    for path in paths:
        try:
            collect(path)
        except Exception as exc:
            failures += 1
            print(f"Supervisor event replay failed: {type(exc).__name__}", file=sys.stderr)
    return failures


def main():
    try:
        collect(sys.argv[1])
    except Exception as exc:
        home = Path(os.environ.get("CUBICLE_HOME", Path.home() / ".cubicle"))
        try:
            (home / "logs").mkdir(mode=0o700, parents=True, exist_ok=True)
            with (home / "logs" / "collector.log").open("a") as stream:
                stream.write(f"Supervisor event ingestion failed: {type(exc).__name__}\n")
        except OSError:
            pass
        raise


if __name__ == "__main__":
    main()
