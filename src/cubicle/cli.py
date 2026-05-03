import argparse
import os
import shutil
import sys
from pathlib import Path

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
    # Ensure it's executable if it's a script
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

def init_hooks(agent):
    home_dir = get_agent_home(agent)
    target_dir = home_dir / "hooks"
    
    # We copy the hook files so they are independent of the repo development
    ensure_copy(PACKAGE_ROOT / "agent_hook.py", target_dir / "cubicle_hook.py")
    ensure_copy(PACKAGE_ROOT / "db.py", target_dir / "db.py")
    print(f"Hooks installed for {agent} in {target_dir}")

def clean_hooks(agent):
    home_dir = get_agent_home(agent)
    target_dir = home_dir / "hooks"
    
    for name in ["cubicle_hook.py", "db.py"]:
        path = target_dir / name
        if path.exists():
            path.unlink()
            print(f"Removed {path}")

def main():
    parser = argparse.ArgumentParser(description="Cubicle: AI Agent Hook Manager")
    subparsers = parser.add_subparsers(dest="command")
    
    # Init hooks command
    init_parser = subparsers.add_parser("init-hooks", help="Initialize agent hooks")
    init_parser.add_argument("--agent", required=True, help="Agent name (claude, gemini, etc.)")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Remove cubicle hooks from an agent")
    clean_parser.add_argument("--agent", required=True, help="Agent name")
    
    args = parser.parse_args()
    
    if args.command == "init-hooks":
        init_hooks(args.agent)
    elif args.command == "clean":
        clean_hooks(args.agent)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
