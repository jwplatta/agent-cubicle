#!/usr/bin/env python3
import sys
import json
import os
from pathlib import Path

import yaml

# Ensure the directory containing this script is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import insert_telemetry

def get_llm_family(payload):
    # Check environment variables
    if os.environ.get("GEMINI_CWD") or os.environ.get("GEMINI_PROJECT_DIR"):
        return "gemini"
    if os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("CLAUDE_ENV_FILE"):
        return "claude"
    if (
        os.environ.get("CODEX_PROJECT_DIR")
        or os.environ.get("CODEX_CWD")
        or os.environ.get("CODEX_SESSION_ID")
        or os.environ.get("CODEX_THREAD_ID")
        or os.environ.get("CODEX_HOME")
        or os.environ.get("CODEX_SANDBOX")
    ):
        return "codex"
    if os.environ.get("COPILOT_PROJECT_DIR") or os.environ.get("COPILOT_SESSION_ID"):
        return "copilot"

    # Check payload keys when env detection is unavailable.
    transcript_path = payload.get("transcript_path", "")
    if isinstance(transcript_path, str):
        if "/.codex/" in transcript_path:
            return "codex"
        if "/.claude/" in transcript_path:
            return "claude"

    # Codex hook payloads consistently use hook_event_name and a cwd field.
    if payload.get("hook_event_name") and payload.get("cwd"):
        return "codex"

    # Default if unknown
    return "unknown"

def _load_event_mapping(agent):
    config_path = Path.home() / ".cubicle" / "config.yaml"
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    known_events = set(cfg["events"])
    mapping = cfg["agents"][agent]["event_mapping"]
    invalid = {k: v for k, v in mapping.items() if v not in known_events}
    if invalid:
        raise ValueError(f"Invalid cubicle event names in mapping for {agent}: {invalid}")
    return mapping

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            return
        
        payload = json.loads(input_data)

        llm_family = get_llm_family(payload)
        # Standardize event name
        native_event = payload.get("hook_event_name") or payload.get("event")
        normalized_event = native_event.lower() if native_event else "unknown"
        if llm_family != "unknown":
            event_mapping = _load_event_mapping(llm_family)
            normalized_event = event_mapping.get(native_event, normalized_event)

        session_id = payload.get("session_id")
        model = payload.get("model")
        
        # Insert into DB
        insert_telemetry(
            session_id=session_id,
            llm_family=llm_family,
            event_type=normalized_event,
            model=model,
            raw_payload=payload
        )
        
        # Output to stdout (no-op for the agent)
        # We must output a valid JSON object
        print(json.dumps({}))
        
    except Exception as e:
        # Don't break the agent on error
        pass

if __name__ == "__main__":
    main()
