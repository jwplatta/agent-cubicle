#!/bin/bash
# Google Gemini agent entry script with language support

# Get language parameter (default to "node" if not specified)
LANGUAGE="${1:-node}"

# Source common base configuration
source /entry-base.sh

echo "Gemini environment ready"

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
