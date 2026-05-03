#!/usr/bin/env python3
import sys
import json
import os
from db import insert_telemetry

def get_llm_family():
    if os.environ.get("GEMINI_CWD"):
        return "gemini"
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        return "claude"
    # Codex? We'll assume if neither but we might need a better check.
    return "codex"

EVENT_MAPPING = {
    "SessionStart": "session_start",
    "SessionEnd": "session_end",
    "BeforeTool": "pre_tool_use",
    "PreToolUse": "pre_tool_use",
    "AfterTool": "post_tool_use",
    "PostToolUse": "post_tool_use",
    "BeforeModel": "pre_model",
    "AfterModel": "post_model",
    "BeforeAgent": "user_prompt_submit",
    "UserPromptSubmit": "user_prompt_submit",
    "Stop": "session_end",
}

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            return
        
        payload = json.loads(input_data)
        
        # Standardize event name
        native_event = payload.get("hook_event_name") or payload.get("event")
        normalized_event = EVENT_MAPPING.get(native_event, native_event.lower() if native_event else "unknown")
        
        llm_family = get_llm_family()
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
