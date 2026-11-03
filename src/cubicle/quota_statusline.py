"""Capture Antigravity's status-line quota without storing conversation content."""

import json
import os
import sys
import tempfile
import time
from pathlib import Path


def record(home, payload):
    quotas = payload.get("quota") or {}
    values = {str(name): float(data["remaining_fraction"])
              for name, data in quotas.items() if isinstance(data, dict)
              and not data.get("disabled", False)
              and isinstance(data.get("remaining_fraction"), (int, float))
              and not isinstance(data.get("remaining_fraction"), bool)
              and 0 <= data["remaining_fraction"] <= 1}
    if not values:
        return False
    directory = Path(home) / "usage"
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(dir=directory, prefix=".agy-")
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump({"observed_at": time.time(), "remaining_fractions": values}, stream)
        os.replace(name, directory / "agy.json")
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return True


def main():
    try:
        payload = json.load(sys.stdin)
        home = os.environ.get("CUBICLE_HOME", str(Path.home() / ".cubicle"))
        record(home, payload)
    except (OSError, ValueError, TypeError):
        pass  # Never break the interactive status line.
    print("Cubicle quota monitoring")


if __name__ == "__main__":
    main()
