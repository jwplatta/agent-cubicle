#!/bin/bash

# Read JSON input from stdin containing tool execution data
data=$(cat)

# Extract command from the tool input
command=$(echo "$data" | jq -r '.tool_input.command // ""')

# Only log if it's a Python script execution in the quant-tutor skills
if [[ "$command" == *"quant-tutor/skills"* && "$command" == *"python"* ]]; then
  # Extract relevant fields
  tool_name=$(echo "$data" | jq -r '.tool_name // "Unknown"')
  description=$(echo "$data" | jq -r '.tool_input.description // "No description"')
  exit_code=$(echo "$data" | jq -r '.tool_response.exit_code // -1')
  stdout=$(echo "$data" | jq -r '.tool_response.stdout // ""')
  stderr=$(echo "$data" | jq -r '.tool_response.stderr // ""')

  # Determine which skill was executed
  skill_name="unknown"
  if [[ "$command" == *"/probability/"* ]]; then
    skill_name="probability"
  elif [[ "$command" == *"/calculus/"* ]]; then
    skill_name="calculus"
  elif [[ "$command" == *"/finance/"* ]]; then
    skill_name="finance"
  fi

  # Extract script name
  script_name=$(basename "$command" 2>/dev/null | awk '{print $1}' || echo "unknown")

  # Define log files
  LOG_DIR="$HOME/.claude/logs/quant-tutor"
  mkdir -p "$LOG_DIR"
  JSONL_LOG="$LOG_DIR/skill-executions.jsonl"
  READABLE_LOG="$LOG_DIR/skill-executions.log"

  # Create timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  # Create structured JSON log entry
  log_entry=$(jq -cn \
    --arg timestamp "$timestamp" \
    --arg tool "$tool_name" \
    --arg skill "$skill_name" \
    --arg script "$script_name" \
    --arg command "$command" \
    --arg description "$description" \
    --arg exit_code "$exit_code" \
    --arg stdout "$stdout" \
    --arg stderr "$stderr" \
    '{
      timestamp: $timestamp,
      tool: $tool,
      skill: $skill,
      script: $script,
      description: $description,
      command: $command,
      exit_code: ($exit_code | tonumber),
      stdout: $stdout,
      stderr: $stderr,
      success: (($exit_code | tonumber) == 0)
    }')

  # Append as JSONL (JSON Lines) format
  echo "$log_entry" >> "$JSONL_LOG"

  # Also create human-readable log entry
  echo "[$timestamp] Quant-Tutor Skill Execution" >> "$READABLE_LOG"
  echo "Skill: $skill_name" >> "$READABLE_LOG"
  echo "Script: $script_name" >> "$READABLE_LOG"
  echo "Description: $description" >> "$READABLE_LOG"
  echo "Command: $command" >> "$READABLE_LOG"
  echo "Exit Code: $exit_code" >> "$READABLE_LOG"
  echo "Output: $stdout" >> "$READABLE_LOG"
  if [ ! -z "$stderr" ]; then
    echo "Errors: $stderr" >> "$READABLE_LOG"
  fi
  echo "---" >> "$READABLE_LOG"
fi

# Always exit successfully so Claude continues normally
exit 0
