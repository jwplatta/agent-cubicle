#!/bin/bash
# Claude Code agent entry script with language support

# Get language parameter (default to "node" if not specified)
LANGUAGE="${1:-node}"

# Source common base configuration
source /entry-base.sh

# Claude-specific: Add MCP servers
echo "Adding MCP servers..."

# Only add if not already present
if ! claude mcp list 2>/dev/null | grep -q "obsidian-mcp"; then
  claude mcp add --scope user --transport stdio obsidian-mcp node /obsidian-mcp/build/index.js
fi

if [ -n "${TODOIST_TOKEN}" ]; then
  echo "TODOIST_TOKEN is set"
  if ! claude mcp list 2>/dev/null | grep -q "todoist"; then
    claude mcp add --scope user --header "Authorization: Bearer ${TODOIST_TOKEN}" --transport http todoist https://ai.todoist.net/mcp
  fi
fi

if [ -n "${GITHUB_TOKEN}" ]; then
  echo "GITHUB_TOKEN is set"
  if ! claude mcp list 2>/dev/null | grep -q "github"; then
    claude mcp add --scope user --header "Authorization: Bearer ${GITHUB_TOKEN}" --transport http github https://api.githubcopilot.com/mcp/
  fi
fi

echo "MCP servers configured. Current list:"
claude mcp list

# Language-specific setup
case "$LANGUAGE" in
  python)
    echo "Python environment:"
    export PATH="/home/$(whoami)/.cargo/bin:${PATH}"
    python3 --version
    uv --version
    ;;
  ruby)
    echo "Ruby environment:"
    ruby --version
    bundler --version
    ;;
  node)
    echo "Node.js environment:"
    node --version
    npm --version
    ;;
  *)
    echo "Unknown language: $LANGUAGE (using defaults)"
    ;;
esac

# Keep container running
tail -f /dev/null
