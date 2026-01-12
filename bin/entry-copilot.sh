#!/bin/bash

if [ -d "/obsidian-mcp" ]; then
  cd /obsidian-mcp
  npm install --silent
  npm run build --silent
  npm link --silent
  cd /cubicle
fi

mkdir -p /root/.copilot/agents

tail -f /dev/null