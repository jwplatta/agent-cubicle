#!/usr/bin/env python3
import sys
import json
from pathlib import Path


def _load_event_mapping():
    import yaml

    config_path = Path.home() / ".cubicle" / "config.yaml"
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    return cfg["agents"]["agy"]["event_mapping"]


def _hook_response(native_event):
    """Return the JSON shape required by Antigravity for each lifecycle event."""
    if native_event == "PreToolUse":
        return {"decision": "allow"}
    if native_event == "Stop":
        # Only "continue" prevents stopping; any other decision permits it.
        return {"decision": "allow"}
    # PostToolUse must return {}, and an empty object is also valid for the
    # optional output fields of PreInvocation and PostInvocation.
    return {}


def _normalize_event(native_event, event_mapping):
    # BeforeTool was used by the original Cubicle proof of concept. Retain it
    # only as a fallback for old direct invocations; Antigravity sends
    # PreToolUse as the command argument.
    legacy_event_aliases = {"BeforeTool": "PreToolUse", "AfterTool": "PostToolUse"}
    native_event = legacy_event_aliases.get(native_event, native_event)
    return event_mapping.get(
        native_event, native_event.lower() if native_event else "unknown"
    )


def main():
    native_event = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        input_data = sys.stdin.read()
        if not input_data:
            return

        sys.path.insert(0, str(Path(__file__).parent))
        from db import insert_telemetry

        payload = json.loads(input_data)

        # agy passes the event name as a CLI arg since it is not in the payload.
        # Keep the payload fallback for direct/legacy invocations.
        native_event = native_event or payload.get("hook_event_name") or payload.get("event")
        event_mapping = _load_event_mapping()
        normalized_event = _normalize_event(native_event, event_mapping)

        insert_telemetry(
            session_id=payload.get("conversationId") or payload.get("session_id"),
            event_type=normalized_event,
            model=payload.get("modelName") or payload.get("model"),
            raw_payload=payload,
        )

    except Exception:
        pass
    finally:
        # Hooks must always emit valid JSON on stdout. In particular, emitting
        # a PreToolUse decision for PostToolUse makes Antigravity reject hooks.
        print(json.dumps(_hook_response(native_event)))


if __name__ == "__main__":
    main()
