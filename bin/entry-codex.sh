#!/bin/bash

if [ -d "/obsidian-mcp" ]; then
  cd /obsidian-mcp
  npm install --silent
  npm run build --silent
  npm link --silent
  cd /workspace
fi

tail -f /dev/null
