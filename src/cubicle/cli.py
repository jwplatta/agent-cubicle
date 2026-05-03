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
                
                # Check if this specific hook is already in the array
                hook_exists = any(h.get("command") == str(hook_script) for h in entry["hooks"])
                if not hook_exists:
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
    # Minimal TOML injection since full round-trip with comments is hard with basic libs
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

def init_hooks(agent):
    home_dir = get_agent_home(agent)
    target_dir = home_dir / "hooks"
    hook_script = target_dir / "cubicle_hook.py"
    
    # 1. Copy files
    ensure_copy(PACKAGE_ROOT / "agent_hook.py", hook_script)
    ensure_copy(PACKAGE_ROOT / "db.py", target_dir / "db.py")
    
    # 2. Register in settings
    events = ["SessionStart", "SessionEnd", "PreToolUse", "PostToolUse", "Stop"]
    if agent == "gemini":
        events = ["SessionStart", "BeforeTool", "AfterTool", "BeforeAgent"]
        update_json_settings(home_dir / "settings.json", hook_script, events)
    elif agent == "claude":
        update_json_settings(home_dir / "settings.json", hook_script, events)
    elif agent == "codex":
        update_codex_toml(home_dir / "config.toml", hook_script, events)
    
    print(f"Hooks installed and registered for {agent}")

def del_hooks(agent):
    home_dir = get_agent_home(agent)
    target_dir = home_dir / "hooks"
    hook_script = target_dir / "cubicle_hook.py"
    
    # 1. Remove files
    for name in ["cubicle_hook.py", "db.py"]:
        path = target_dir / name
        if path.exists():
            path.unlink()
            print(f"Removed {path}")

    # 2. Unregister from settings (Optional but cleaner)
    # For now, we'll leave the settings entries; they will just point to missing files 
    # and agents generally handle this gracefully (or we can add cleanup logic if requested).

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
