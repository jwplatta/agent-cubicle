#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

print_help() {
  cat <<'EOF'
agent-cubicle: run a local coding agent with repo-managed config

Usage:
  agent-cubicle run --agent <codex|claude|copilot|gemini> --project <name>
  agent-cubicle clean --agent <codex|claude|copilot|gemini>
  agent-cubicle help
  agent-cubicle -h|--help
EOF
}

die() {
  echo "Error: $*" >&2
  exit 1
}

load_env() {
  if [[ ! -f "$ROOT_DIR/.env" ]]; then
    die "Missing .env in repo root. Create it and set PROJECTS_DIR."
  fi
  set -a
  # shellcheck source=/dev/null
  source "$ROOT_DIR/.env"
  set +a
  if [[ -z "${PROJECTS_DIR:-}" ]]; then
    die "PROJECTS_DIR is not set. Add it to .env."
  fi
}

ensure_symlink() {
  local source="$1"
  local target="$2"

  if [[ ! -e "$source" ]]; then
    die "Source path does not exist: $source"
  fi

  if [[ -e "$target" || -L "$target" ]]; then
    if [[ -L "$target" ]]; then
      local existing
      existing="$(readlink "$target")"
      if [[ "$existing" == "$source" ]]; then
        return 0
      fi
      die "Target already exists as a different symlink: $target -> $existing"
    fi
    die "Target already exists and is not a symlink: $target"
  fi

  mkdir -p "$(dirname "$target")"
  ln -s "$source" "$target"
}

remove_symlink_if_matches() {
  local source="$1"
  local target="$2"

  if [[ -L "$target" ]]; then
    local existing
    existing="$(readlink "$target")"
    if [[ "$existing" == "$source" ]]; then
      rm "$target"
    fi
  fi
}

link_shared() {
  local agent="$1"
  local home_dir="$2"
  local src_dir=""
  local target_dir=""
  local shopt_nullglob="off"

  shopt -q nullglob && shopt_nullglob="on"
  shopt -s nullglob

  src_dir="$ROOT_DIR/skills"
  target_dir="$home_dir/skills"
  if [[ -d "$src_dir" ]]; then
    mkdir -p "$target_dir"
    for entry in "$src_dir"/*; do
      [[ -e "$entry" ]] || continue
      ensure_symlink "$entry" "$target_dir/$(basename "$entry")"
    done
  fi

  src_dir="$ROOT_DIR/commands"
  target_dir="$home_dir/commands"
  if [[ -d "$src_dir" ]]; then
    mkdir -p "$target_dir"
    for entry in "$src_dir"/*; do
      [[ -f "$entry" ]] || continue
      ensure_symlink "$entry" "$target_dir/$(basename "$entry")"
    done
  fi

  if [[ "$shopt_nullglob" == "off" ]]; then
    shopt -u nullglob
  fi
}

link_configs() {
  local agent="$1"
  local home_dir="$2"

  case "$agent" in
    claude)
      ensure_symlink "$ROOT_DIR/configs/claude/settings.json" "$home_dir/settings.json"
      ;;
    codex)
      ensure_symlink "$ROOT_DIR/configs/codex/config.toml" "$home_dir/config.toml"
      ;;
    gemini)
      ensure_symlink "$ROOT_DIR/configs/gemini/settings.json" "$home_dir/settings.json"
      ensure_symlink "$ROOT_DIR/configs/gemini/trusted_hooks.json" "$home_dir/trusted_hooks.json"
      ;;
    copilot)
      ensure_symlink "$ROOT_DIR/configs/copilot/config.json" "$home_dir/config.json"
      ensure_symlink "$ROOT_DIR/configs/copilot/mcp-config.json" "$home_dir/mcp-config.json"
      ;;
    *)
      die "Unknown agent: $agent"
      ;;
  esac
}

clean_shared() {
  local agent="$1"
  local home_dir="$2"
  local src_dir=""
  local target_dir=""

  src_dir="$ROOT_DIR/skills"
  target_dir="$home_dir/skills"
  if [[ -d "$src_dir" ]]; then
    for entry in "$src_dir"/*; do
      [[ -e "$entry" ]] || continue
      remove_symlink_if_matches "$entry" "$target_dir/$(basename "$entry")"
    done
  fi

  src_dir="$ROOT_DIR/commands"
  target_dir="$home_dir/commands"
  if [[ -d "$src_dir" ]]; then
    for entry in "$src_dir"/*; do
      [[ -f "$entry" ]] || continue
      remove_symlink_if_matches "$entry" "$target_dir/$(basename "$entry")"
    done
  fi
}

clean_configs() {
  local agent="$1"
  local home_dir="$2"

  case "$agent" in
    claude)
      remove_symlink_if_matches "$ROOT_DIR/configs/claude/settings.json" "$home_dir/settings.json"
      ;;
    codex)
      remove_symlink_if_matches "$ROOT_DIR/configs/codex/config.toml" "$home_dir/config.toml"
      ;;
    gemini)
      remove_symlink_if_matches "$ROOT_DIR/configs/gemini/settings.json" "$home_dir/settings.json"
      remove_symlink_if_matches "$ROOT_DIR/configs/gemini/trusted_hooks.json" "$home_dir/trusted_hooks.json"
      ;;
    copilot)
      remove_symlink_if_matches "$ROOT_DIR/configs/copilot/config.json" "$home_dir/config.json"
      remove_symlink_if_matches "$ROOT_DIR/configs/copilot/mcp-config.json" "$home_dir/mcp-config.json"
      ;;
    *)
      die "Unknown agent: $agent"
      ;;
  esac
}

run_agent() {
  local agent="$1"
  local project="$2"
  local home_dir=""
  local agent_cmd=""

  case "$agent" in
    claude) home_dir="$HOME/.claude"; agent_cmd="claude" ;;
    codex) home_dir="$HOME/.codex"; agent_cmd="codex" ;;
    gemini) home_dir="$HOME/.gemini"; agent_cmd="gemini" ;;
    copilot) home_dir="$HOME/.copilot"; agent_cmd="copilot" ;;
    *) die "Unknown agent: $agent" ;;
  esac

  link_shared "$agent" "$home_dir"
  link_configs "$agent" "$home_dir"

  local project_dir="$PROJECTS_DIR/$project"
  if [[ ! -d "$project_dir" ]]; then
    die "Project directory does not exist: $project_dir"
  fi

  cd "$project_dir"
  exec "$agent_cmd"
}

clean_agent() {
  local agent="$1"
  local home_dir=""

  case "$agent" in
    claude) home_dir="$HOME/.claude" ;;
    codex) home_dir="$HOME/.codex" ;;
    gemini) home_dir="$HOME/.gemini" ;;
    copilot) home_dir="$HOME/.copilot" ;;
    *) die "Unknown agent: $agent" ;;
  esac

  clean_shared "$agent" "$home_dir"
  clean_configs "$agent" "$home_dir"
}

command="${1:-help}"
shift || true

case "$command" in
  run)
    agent=""
    project=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --agent)
          agent="${2:-}"
          shift 2
          ;;
        --project)
          project="${2:-}"
          shift 2
          ;;
        -h|--help)
          print_help
          exit 0
          ;;
        *)
          die "Unknown argument: $1"
          ;;
      esac
    done

    [[ -n "$agent" ]] || die "Missing --agent"
    [[ -n "$project" ]] || die "Missing --project"

    load_env
    run_agent "$agent" "$project"
    ;;
  clean)
    agent=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --agent)
          agent="${2:-}"
          shift 2
          ;;
        -h|--help)
          print_help
          exit 0
          ;;
        *)
          die "Unknown argument: $1"
          ;;
      esac
    done

    [[ -n "$agent" ]] || die "Missing --agent"
    clean_agent "$agent"
    ;;
  help|-h|--help)
    print_help
    ;;
  *)
    die "Unknown command: $command"
    ;;
esac
