#!/usr/bin/env python3
import re
import sys
import json
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from db import insert_telemetry

_MODEL_LABEL_RE = re.compile(r'label="([^"]+)"')


def _load_event_mapping():
    config_path = Path.home() / ".cubicle" / "config.yaml"
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    return cfg["agents"]["agy"]["event_mapping"]


def _read_model_from_log():
    log_dir = Path.home() / ".gemini" / "antigravity-cli" / "log"
    logs = sorted(log_dir.glob("cli-*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not logs:
        return None
    try:
        text = logs[0].read_text(errors="replace")
        matches = _MODEL_LABEL_RE.findall(text)
        return matches[-1] if matches else None
    except OSError:
        return None


def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            return

        payload = json.loads(input_data)

        native_event = payload.get("hook_event_name") or payload.get("event")
        event_mapping = _load_event_mapping()
        normalized_event = event_mapping.get(
            native_event, native_event.lower() if native_event else "unknown"
        )

        insert_telemetry(
            session_id=payload.get("conversationId") or payload.get("session_id"),
            event_type=normalized_event,
            model=_read_model_from_log(),
            raw_payload=payload,
        )

        print(json.dumps({}))

    except Exception:
        pass


if __name__ == "__main__":
    main()
