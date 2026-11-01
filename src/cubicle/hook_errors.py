"""Report telemetry-hook failures without leaking payloads or blocking agents."""

import sys
from datetime import datetime, timezone
from pathlib import Path


def report(error):
    message = f"{datetime.now(timezone.utc).isoformat()} telemetry hook failed: {type(error).__name__}"
    try:
        path = Path.home() / ".cubicle" / "logs" / "hooks.log"
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(message + "\n")
    except OSError:
        pass
    print(message, file=sys.stderr)
