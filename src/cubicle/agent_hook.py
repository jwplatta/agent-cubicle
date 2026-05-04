#!/usr/bin/env python3
import sys
import json
import os
from pathlib import Path

import yaml

# Ensure the directory containing this script is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import insert_telemetry

SUPPORTED_LLM_FAMILIES = {"claude", "gemini", "codex", "copilot"}


def get_llm_family(payload):
    family = os.environ.get("CUBICLE_LLM_FAMILY", "").strip().lower()
    if family in SUPPORTED_LLM_FAMILIES:
        return family
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
