import argparse
import json
import os
import shutil
import sys
from pathlib import Path

# Try to import tomli/tomllib for TOML handling
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

# Define the root of the cubicle installation
PACKAGE_ROOT = Path(__file__).parent
CUBICLE_HOME = Path.home() / ".cubicle"
HOOKS_INSTALL_DIR = CUBICLE_HOME / "hooks"

def die(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)

def ensure_copy(source, target):
    source = Path(source).absolute()
    target = Path(target).absolute()
    
    if not source.exists():
        die(f"Source path does not exist: {source}")
        
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    # Ensure it's executable
    if source.suffix == ".py" or source.suffix == ".sh":
        target.chmod(target.stat().st_mode | 0o111)

def get_agent_home(agent):
    homes = {
        "claude": Path.home() / ".claude",
        "codex": Path.home() / ".codex",
        "gemini": Path.home() / ".gemini",
        "copilot": Path.home() / ".copilot",
    }
    if agent not in homes:
        die(f"Unknown agent: {agent}")
    return homes[agent]

def update_json_settings(settings_path, hook_script, events):
    if not settings_path.exists():
        settings = {}
    else:
        with open(settings_path, "r") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = {}

    if "hooks" not in settings:
        settings["hooks"] = {}
    
    hooks_config = settings["hooks"]
    if isinstance(hooks_config, dict) and "enabled" not in hooks_config:
        hooks_config["enabled"] = True

    for event in events:
        if event not in hooks_config:
            hooks_config[event] = []
        
        # Check if already registered
        matcher_found = False
        for entry in hooks_config[event]:
            if entry.get("matcher") == "*":
                matcher_found = True
                if "hooks" not in entry:
                    entry["hooks"] = []
                
                # Remove any existing cubicle-telemetry hooks to ensure only one remains with the new path
                entry["hooks"] = [h for h in entry["hooks"] if h.get("name") != "cubicle-telemetry"]
                
                entry["hooks"].append({
                    "name": "cubicle-telemetry",
                    "type": "command",
                    "command": str(hook_script),
                    "description": "Cubicle unified agent telemetry"
                })
                break
        
        if not matcher_found:
            hooks_config[event].append({
                "matcher": "*",
                "hooks": [{
                    "name": "cubicle-telemetry",
                    "type": "command",
                    "command": str(hook_script),
                    "description": "Cubicle unified agent telemetry"
                }]
            })

    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)

def update_codex_toml(config_path, hook_script, events):
    # Minimal TOML injection
    if not config_path.exists():
        content = "[features]\ncodex_hooks = true\n\n"
    else:
        with open(config_path, "r") as f:
            content = f.read()

    if "codex_hooks = true" not in content:
        if "[features]" in content:
            content = content.replace("[features]", "[features]\ncodex_hooks = true")
        else:
            content = "[features]\ncodex_hooks = true\n\n" + content

    for event in events:
        hook_block = f'\n[[hooks.{event}]]\nmatcher = "*"\n\n[[hooks.{event}.hooks]]\nname = "cubicle-telemetry"\ntype = "command"\ncommand = "{hook_script}"\ndescription = "Cubicle unified agent telemetry"\n'
        if str(hook_script) not in content or f"hooks.{event}" not in content:
            content += hook_block

    with open(config_path, "w") as f:
        f.write(content)

def remove_json_settings(settings_path, hook_script):
    if not settings_path.exists():
        return

    with open(settings_path, "r") as f:
        try:
            settings = json.load(f)
        except json.JSONDecodeError:
            return

    if "hooks" not in settings:
        return
    
    hooks_config = settings["hooks"]
    if not isinstance(hooks_config, dict):
        return

    modified = False
    for event in list(hooks_config.keys()):
        if event == "enabled" or event == "disabled":
            continue
            
        if not isinstance(hooks_config[event], list):
            continue

        new_matcher_groups = []
        for entry in hooks_config[event]:
            if "hooks" in entry:
                # Filter out the cubicle hook
                original_count = len(entry["hooks"])
                entry["hooks"] = [h for h in entry["hooks"] if h.get("command") == str(hook_script) or "cubicle_hook.py" in h.get("command", "")]
                
                # Check if we should actually be removing it
                entry["hooks"] = [h for h in entry["hooks"] if not (h.get("command") == str(hook_script) or "cubicle_hook.py" in h.get("command", ""))]
                
                # Wait, the logic above is wrong. Let's fix it.
                # Actually, I'll just rewrite the filter part.
                
                new_hooks = [h for h in entry.get("hooks", []) if h.get("name") != "cubicle-telemetry"]
                if len(new_hooks) != len(entry.get("hooks", [])):
                    modified = True
                entry["hooks"] = new_hooks
                
            # Only keep the matcher group if it still has hooks
            if entry.get("hooks"):
                new_matcher_groups.append(entry)
            else:
                modified = True
        
        hooks_config[event] = new_matcher_groups
        
        # Remove the event entirely if no matcher groups left
        if not hooks_config[event]:
            del hooks_config[event]
            modified = True

    if modified:
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)
        print(f"Unregistered hooks from {settings_path}")

def remove_codex_toml(config_path, hook_script):
    if not config_path.exists():
        return

    with open(config_path, "r") as f:
        lines = f.readlines()

    # Simple heuristic-based filtering for TOML
    new_lines = []
    modified = False
    skip_mode = False
    
    for line in lines:
        if line.startswith("[[hooks.") and "cubicle-telemetry" in "".join(lines[lines.index(line):lines.index(line)+10]):
            skip_mode = True
            modified = True
            continue
        
        if skip_mode:
            if line.startswith("[[hooks.") or line.startswith("[projects.") or line.startswith("[features]"):
                skip_mode = False
            else:
                continue
                
        if "cubicle-telemetry" in line:
            modified = True
            continue

        new_lines.append(line)

    if modified:
        content = "".join(new_lines).replace("\n\n\n", "\n\n")
        with open(config_path, "w") as f:
            f.write(content)
        print(f"Unregistered hooks from {config_path}")

def init_hooks(agent):
    # 1. Ensure centralized hooks directory exists and has fresh copies
    HOOKS_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    central_hook = HOOKS_INSTALL_DIR / "cubicle_hook.py"
    central_db = HOOKS_INSTALL_DIR / "db.py"
    
    ensure_copy(PACKAGE_ROOT / "agent_hook.py", central_hook)
    ensure_copy(PACKAGE_ROOT / "db.py", central_db)
    
    # 2. Register this centralized path in agent settings
    home_dir = get_agent_home(agent)
    events = ["SessionStart", "SessionEnd", "PreToolUse", "PostToolUse", "Stop"]
    
    if agent == "gemini":
        events = ["SessionStart", "BeforeTool", "AfterTool", "BeforeAgent"]
        update_json_settings(home_dir / "settings.json", central_hook, events)
    elif agent == "claude":
        update_json_settings(home_dir / "settings.json", central_hook, events)
    elif agent == "codex":
        update_codex_toml(home_dir / "config.toml", central_hook, events)
    
    # 3. Clean up legacy per-agent hooks if they exist
    legacy_hook = home_dir / "hooks" / "cubicle_hook.py"
    legacy_db = home_dir / "hooks" / "db.py"
    if legacy_hook.exists(): legacy_hook.unlink()
    if legacy_db.exists(): legacy_db.unlink()
    
    print(f"Hooks centralized at {central_hook} and registered for {agent}")

def del_hooks(agent):
    home_dir = get_agent_home(agent)
    central_hook = HOOKS_INSTALL_DIR / "cubicle_hook.py"
    
    # 1. Unregister from settings using the centralized path
    if agent == "gemini":
        remove_json_settings(home_dir / "settings.json", central_hook)
    elif agent == "claude":
        remove_json_settings(home_dir / "settings.json", central_hook)
    elif agent == "codex":
        remove_codex_toml(home_dir / "config.toml", central_hook)

    # 2. Clean up any legacy per-agent files that might still be there
    legacy_dir = home_dir / "hooks"
    for name in ["cubicle_hook.py", "db.py"]:
        path = legacy_dir / name
        if path.exists():
            path.unlink()
            print(f"Removed legacy file {path}")

def main():
    parser = argparse.ArgumentParser(description="Cubicle: AI Agent Hook Manager")
    subparsers = parser.add_subparsers(dest="command")
    
    # Init hooks command
    init_parser = subparsers.add_parser("init-hooks", help="Initialize agent hooks")
    init_parser.add_argument("--agent", required=True, help="Agent name (claude, gemini, etc.)")
    
    # Del hooks command
    del_parser = subparsers.add_parser("del-hooks", help="Remove cubicle hooks from an agent")
    del_parser.add_argument("--agent", required=True, help="Agent name")
    
    args = parser.parse_args()
    
    if args.command == "init-hooks":
        init_hooks(args.agent)
    elif args.command == "del-hooks":
        del_hooks(args.agent)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
