#!/usr/bin/env python3
import sys
import json
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from db import insert_telemetry


def _load_event_mapping():
    config_path = Path.home() / ".cubicle" / "config.yaml"
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    return cfg["agents"]["agy"]["event_mapping"]


def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            return

        payload = json.loads(input_data)

        # agy passes the event name as a CLI arg since it's not in the payload
        native_event = sys.argv[1] if len(sys.argv) > 1 else None
        event_mapping = _load_event_mapping()
        normalized_event = event_mapping.get(
            native_event, native_event.lower() if native_event else "unknown"
        )

        insert_telemetry(
            session_id=payload.get("conversationId") or payload.get("session_id"),
            event_type=normalized_event,
            model=payload.get("modelName"),
            raw_payload=payload,
        )

        print(json.dumps({}))

    except Exception:
        pass


if __name__ == "__main__":
    main()
