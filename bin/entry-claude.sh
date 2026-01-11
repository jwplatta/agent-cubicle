#!/bin/bash

if [ -d "/obsidian-mcp" ]; then
  cd /obsidian-mcp
  npm install --silent
  npm run build --silent
  npm link --silent
  cd /cubicle
fi

echo "Adding MCP servers..."

if ! claude mcp list 2>/dev/null | grep -q "obsidian-mcp"; then
  echo "Adding obsidian-mcp server..."
  claude mcp add --transport stdio obsidian-mcp node /obsidian-mcp/build/index.js
fi

if ! claude mcp list 2>/dev/null | grep -q "todoist"; then
  echo "Adding todoist server..."
  if [ -n "${TODOIST_TOKEN}" ]; then
    echo "TODOIST_TOKEN is set"
    claude mcp add --header "Authorization: Bearer ${TODOIST_TOKEN}" --transport http todoist https://ai.todoist.net/mcp
  fi
fi

if ! claude mcp list 2>/dev/null | grep -q "github"; then
  echo "Adding github server..."
  if [ -n "${GITHUB_TOKEN}" ]; then
    echo "GITHUB_TOKEN is set"
    claude mcp add --header "Authorization: Bearer ${GITHUB_TOKEN}" --transport http github https://api.githubcopilot.com/mcp/
  fi
fi

echo "MCP servers configured. Current list:"
claude mcp list

tail -f /dev/null
