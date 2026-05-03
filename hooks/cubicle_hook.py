#!/usr/bin/env python3
import sys
import json
import os
from db import insert_telemetry

def get_llm_family(payload):
    # Check environment variables
    if os.environ.get("GEMINI_CWD") or os.environ.get("GEMINI_PROJECT_DIR"):
        return "gemini"
    if os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("CLAUDE_ENV_FILE"):
        return "claude"
    if os.environ.get("CODEX_PROJECT_DIR"):
        return "codex"
    
    # Check payload keys
    if "hook_event_name" in payload and any(k in payload for k in ["transcript_path", "tool_use"]):
        # Claude/Codex specific keys often found in hooks
        if "PreToolUse" in payload.get("hook_event_name", ""):
             return "claude" # Heuristic
    
    # Default if unknown
    return "unknown"

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
        
        llm_family = get_llm_family(payload)
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
