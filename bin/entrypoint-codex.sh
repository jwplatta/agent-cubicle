#!/bin/bash

# Build and install obsidian-mcp from mounted source
if [ -d "/obsidian-mcp" ]; then
  cd /obsidian-mcp
  npm install --silent
  npm run build --silent
  npm link --silent
  cd /workspace
fi

codex mcp add obsidian-mcp -- node /obsidian-mcp/build/index.js 2>/dev/null || true

tail -f /dev/null
