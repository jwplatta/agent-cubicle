#!/bin/bash

if [ -d "/obsidian-mcp" ]; then
  cd /obsidian-mcp
  npm install --silent
  npm run build --silent
  npm link --silent
  cd /cubicle
fi

mkdir -p /root/.copilot

envsubst < /cubicle/repos/agent-cubicle/config/copilot/mcp-config.json.template > /root/.copilot/mcp-config.json

tail -f /dev/null