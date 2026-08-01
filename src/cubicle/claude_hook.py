#!/usr/bin/env python3
import sys
import json
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from db import insert_telemetry, get_model_for_session


def _load_event_mapping():
    config_path = Path.home() / ".cubicle" / "config.yaml"
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    return cfg["agents"]["claude"]["event_mapping"]


def resolve_model(payload):
    model = payload.get("model")
    if not model:
        model = get_model_for_session(payload.get("session_id"))
    return model


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

        session_id = payload.get("session_id")
        model = resolve_model(payload)

        insert_telemetry(
            session_id=session_id,
            event_type=normalized_event,
            model=model,
            raw_payload=payload,
        )

        print(json.dumps({}))

    except Exception:
        pass


if __name__ == "__main__":
    main()
