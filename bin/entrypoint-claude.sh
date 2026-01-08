#!/bin/bash

if [ -d "/obsidian-mcp" ]; then
  cd /obsidian-mcp
  npm install --silent
  npm run build --silent
  npm link --silent
  cd /workspace
fi

claude mcp add --transport stdio obsidian-mcp node /obsidian-mcp/build/index.js 2>/dev/null || true

tail -f /dev/null
