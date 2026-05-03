import argparse
import os
import shutil
import sys
from pathlib import Path
from dotenv import load_dotenv

# Define the root of the cubicle installation
# This works whether running from source or installed
PACKAGE_ROOT = Path(__file__).parent

def die(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)

def load_config():
    # Try to load .env from current directory or home
    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        env_path = Path.home() / ".cubicle" / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
    
    projects_dir = os.environ.get("PROJECTS_DIR")
    return projects_dir

def ensure_symlink(source, target):
    source = Path(source).absolute()
    target = Path(target).absolute()
    
    if not source.exists():
        die(f"Source path does not exist: {source}")
        
    if target.exists() or target.is_symlink():
        if target.is_symlink() and target.readlink() == source:
            return
        # Backup or remove
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
            
    target.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(source, target)

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

def link_shared(agent, repo_root):
    home_dir = get_agent_home(agent)
    
    # Shared commands usually stay as symlinks to the repo
    # so they can be edited easily. Skills are handled by skillex.
    for folder in ["commands"]:
        src_dir = repo_root / folder
        target_dir = home_dir / folder
        if src_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
            for entry in src_dir.iterdir():
                ensure_symlink(entry, target_dir / entry.name)

def link_configs(agent, repo_root):
    home_dir = get_agent_home(agent)
    config_map = {
        "claude": [("configs/claude/settings.json", "settings.json")],
        "codex": [("configs/codex/config.toml", "config.toml")],
        "gemini": [
            ("configs/gemini/settings.json", "settings.json"),
            ("configs/gemini/trusted_hooks.json", "trusted_hooks.json"),
        ],
        "copilot": [
            ("configs/copilot/config.json", "config.json"),
            ("configs/copilot/mcp-config.json", "mcp-config.json"),
        ],
    }
    
    for src_rel, target_name in config_map.get(agent, []):
        ensure_symlink(repo_root / src_rel, home_dir / target_name)

def run(agent, project):
    projects_dir = load_config()
    if not projects_dir:
        die("PROJECTS_DIR not set in .env")
        
    repo_root = Path(__file__).parents[2] # Adjust based on where cli.py is
    
    link_shared(agent, repo_root)
    link_configs(agent, repo_root)
    # Always ensure hooks are present when running
    init_hooks(agent)
    
    project_path = Path(projects_dir) / project
    if not project_path.exists():
        die(f"Project directory does not exist: {project_path}")
    
    print(f"Launching {agent} in {project_path}...")
    os.chdir(project_path)
    
    # Execute the agent command
    # Assuming the agent command is the same as the agent name
    agent_cmd = agent
    try:
        os.execvp(agent_cmd, [agent_cmd])
    except FileNotFoundError:
        die(f"Agent command '{agent_cmd}' not found in PATH")

def main():
    parser = argparse.ArgumentParser(description="Cubicle: AI Agent Harness")
    subparsers = parser.add_subparsers(dest="command")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run an agent in a project")
    run_parser.add_argument("--agent", required=True, help="Agent name (claude, gemini, etc.)")
    run_parser.add_argument("--project", required=True, help="Project name")
    
    # Init hooks command
    init_parser = subparsers.add_parser("init-hooks", help="Initialize agent hooks")
    init_parser.add_argument("--agent", required=True, help="Agent name")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean agent setup")
    clean_parser.add_argument("--agent", required=True, help="Agent name")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run(args.agent, args.project)
    elif args.command == "init-hooks":
        init_hooks(args.agent)
    elif args.command == "clean":
        home_dir = get_agent_home(args.agent)
        # Add logic to clean shared/configs too if needed
        clean_hooks(args.agent)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
