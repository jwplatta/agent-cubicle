import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
from pathlib import Path

import yaml
from dotenv import dotenv_values

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
CUBICLE_CONFIG = CUBICLE_HOME / "config.yaml"
ENV_FILE = CUBICLE_HOME / ".env"
DEFAULT_CONFIG = PACKAGE_ROOT / "default_config.yaml"
LLM_WRAPPERS = {
    "claude": "claude",
    "gemini": "gemini",
    "codex": "codex",
}
DEFAULT_MLFLOW_GATEWAY_URL = "http://127.0.0.1:5000"
ENV_VAR_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DASHBOARD_PID_FILE = CUBICLE_HOME / "data" / "dashboard.pid"
DEFAULT_DASHBOARD_PORT = 8501

def die(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def ensure_cubicle_home():
    CUBICLE_HOME.mkdir(parents=True, exist_ok=True)


def validate_env_name(name):
    if not ENV_VAR_NAME_RE.match(name):
        die(f"Invalid environment variable name: {name}")


def load_shared_env():
    if not ENV_FILE.exists():
        return {}

    loaded = dotenv_values(ENV_FILE)
    return {key: value if value is not None else "" for key, value in loaded.items()}


def write_shared_env(env_vars):
    ensure_cubicle_home()
    with open(ENV_FILE, "w") as f:
        for key, value in env_vars.items():
            encoded = json.dumps(value)
            f.write(f"{key}={encoded}\n")


def set_env_var(name, value):
    validate_env_name(name)
    env_vars = load_shared_env()
    env_vars[name] = value
    write_shared_env(env_vars)
    print(f"Set {name} in {ENV_FILE}")


def unset_env_var(name):
    validate_env_name(name)
    env_vars = load_shared_env()
    if name in env_vars:
        del env_vars[name]
        write_shared_env(env_vars)
        print(f"Removed {name} from {ENV_FILE}")


def list_env_vars():
    env_vars = load_shared_env()
    for name, value in env_vars.items():
        print(f"{name}={value}")


def mlflow_gateway_url():
    return os.environ.get("CUBICLE_MLFLOW_GATEWAY_URL", DEFAULT_MLFLOW_GATEWAY_URL).rstrip("/")


def apply_mlflow_observability(agent, argv, env):
    gateway_url = mlflow_gateway_url()

    if agent == "gemini":
        env["GOOGLE_GEMINI_BASE_URL"] = f"{gateway_url}/gateway/proxy/gemini-cli"
        return argv
    if agent == "claude":
        env["ANTHROPIC_BASE_URL"] = f"{gateway_url}/gateway/proxy/claude-code"
        return argv
    if agent == "codex":
        return [
            "--config",
            f'openai_base_url="{gateway_url}/gateway/proxy/codex/v1"',
            *argv,
        ]

    die(f"MLflow observability is not configured for '{agent}'")


def launch_agent(agent, argv, observability=False):
    executable = shutil.which(agent)
    if executable is None:
        die(f"Could not find '{agent}' on PATH")

    env = os.environ.copy()
    env.update(load_shared_env())
    env["CUBICLE_LLM_FAMILY"] = agent
    if observability:
        argv = apply_mlflow_observability(agent, argv, env)
    os.execvpe(executable, [agent, *argv], env)


def parse_wrapper_args(argv):
    observability = False
    forwarded = []

    for arg in argv:
        if arg == "--observe":
            observability = True
        else:
            forwarded.append(arg)

    return forwarded, observability

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

def validate_config(cfg):
    known_events = set(cfg.get("events", []))
    if not known_events:
        die("config.yaml is missing the top-level 'events' list")
    errors = []
    for agent, agent_cfg in cfg.get("agents", {}).items():
        for native, canonical in agent_cfg.get("event_mapping", {}).items():
            if canonical not in known_events:
                errors.append(f"  [{agent}] {native} -> '{canonical}' is not a defined cubicle event")
    if errors:
        die("Invalid event mappings in config.yaml:\n" + "\n".join(errors))

def load_config():
    with open(CUBICLE_CONFIG) as f:
        cfg = yaml.safe_load(f)
    validate_config(cfg)
    return cfg

def init_config():
    ensure_cubicle_home()
    (CUBICLE_HOME / "data").mkdir(exist_ok=True)
    if CUBICLE_CONFIG.exists():
        print(f"Config already exists at {CUBICLE_CONFIG}")
        return
    shutil.copy2(DEFAULT_CONFIG, CUBICLE_CONFIG)
    print(f"Created config at {CUBICLE_CONFIG}")

def update_json_settings(agent, settings_path, hook_script, events):
    if not settings_path.exists():
        settings = {}
    else:
        with open(settings_path, "r") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = {}

    # Agent-specific global enablement
    if agent == "gemini":
        if "hooksConfig" not in settings:
            settings["hooksConfig"] = {}
        settings["hooksConfig"]["enabled"] = True
    elif agent == "claude":
        settings["disableAllHooks"] = False

    if "hooks" not in settings:
        settings["hooks"] = {}
    
    hooks_obj = settings["hooks"]
    
    # Ensure hooks_obj is a dict and remove legacy/invalid 'enabled' key
    if not isinstance(hooks_obj, dict):
        settings["hooks"] = {}
        hooks_obj = settings["hooks"]
    
    if "enabled" in hooks_obj:
        del hooks_obj["enabled"]

    for event in events:
        if event not in hooks_obj:
            hooks_obj[event] = []
        
        # Check if already registered
        matcher_found = False
        for entry in hooks_obj[event]:
            if entry.get("matcher") == "*":
                matcher_found = True
                if "hooks" not in entry:
                    entry["hooks"] = []
                
                # Remove any existing cubicle-telemetry hooks to ensure only one remains with the new path
                entry["hooks"] = [h for h in entry["hooks"] if h.get("name") != "cubicle-telemetry"]
                
                entry["hooks"].append({
                    "name": "cubicle-telemetry",
                    "type": "command",
                    "command": f"python3 {hook_script}",
                    "description": "Cubicle unified agent telemetry"
                })
                break
        
        if not matcher_found:
            hooks_obj[event].append({
                "matcher": "*",
                "hooks": [{
                    "name": "cubicle-telemetry",
                    "type": "command",
                    "command": f"python3 {hook_script}",
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

    # Clean up existing cubicle-telemetry blocks first to avoid duplication/stale paths
    lines = content.splitlines()
    new_lines = []
    skip_mode = False
    for line in lines:
        if line.startswith("[[hooks.") and "cubicle-telemetry" in "".join(lines[lines.index(line):lines.index(line)+10]):
            skip_mode = True
            continue
        if skip_mode:
            if line.startswith("[[hooks.") or line.startswith("[projects.") or line.startswith("[features]"):
                skip_mode = False
            else:
                continue
        if "cubicle-telemetry" in line:
            continue
        new_lines.append(line)
    
    content = "\n".join(new_lines)

    # Append fresh blocks
    for event in events:
        hook_block = f'\n[[hooks.{event}]]\nmatcher = "*"\n\n[[hooks.{event}.hooks]]\nname = "cubicle-telemetry"\ntype = "command"\ncommand = "python3 {hook_script}"\ndescription = "Cubicle unified agent telemetry"\n'
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
                # Filter out the cubicle-telemetry hook
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

AGENT_HOOKS = {
    "claude": "claude_hook.py",
    "codex": "codex_hook.py",
    "gemini": "gemini_hook.py",
    "copilot": "claude_hook.py",  # copilot uses same model-resolution pattern as claude
}


def _ensure_resources():
    HOOKS_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    (CUBICLE_HOME / "data").mkdir(parents=True, exist_ok=True)

    for hook_file in set(AGENT_HOOKS.values()):
        ensure_copy(PACKAGE_ROOT / hook_file, HOOKS_INSTALL_DIR / hook_file)
    ensure_copy(PACKAGE_ROOT / "db.py", HOOKS_INSTALL_DIR / "db.py")
    shutil.copy2(DEFAULT_CONFIG, CUBICLE_CONFIG)
    print(f"Synced event config to {CUBICLE_CONFIG}")

def init_hooks(agent=None):
    _ensure_resources()

    if agent:
        hook_script = HOOKS_INSTALL_DIR / AGENT_HOOKS[agent]
        home_dir = get_agent_home(agent)
        cfg = load_config()
        events = list(cfg["agents"][agent]["event_mapping"].keys())

        if agent == "gemini":
            update_json_settings(agent, home_dir / "settings.json", hook_script, events)
        elif agent == "claude":
            update_json_settings(agent, home_dir / "settings.json", hook_script, events)
        elif agent == "codex":
            update_codex_toml(home_dir / "config.toml", hook_script, events)
        elif agent == "copilot":
            update_json_settings(agent, home_dir / "settings.json", hook_script, events)

        print(f"Hooks registered for {agent} pointing to {hook_script}")
    else:
        print("No agent specified. Use --agent <name> to register hooks.")

def del_hooks(agent):
    home_dir = get_agent_home(agent)
    hook_script = HOOKS_INSTALL_DIR / AGENT_HOOKS[agent]

    # Unregister from settings
    if agent == "gemini":
        remove_json_settings(home_dir / "settings.json", hook_script)
    elif agent == "claude":
        remove_json_settings(home_dir / "settings.json", hook_script)
    elif agent == "codex":
        remove_codex_toml(home_dir / "config.toml", hook_script)
    elif agent == "copilot":
        remove_json_settings(home_dir / "settings.json", hook_script)

def start_dashboard(port=DEFAULT_DASHBOARD_PORT):
    CUBICLE_HOME.mkdir(parents=True, exist_ok=True)
    (CUBICLE_HOME / "data").mkdir(exist_ok=True)

    if DASHBOARD_PID_FILE.exists():
        pid = int(DASHBOARD_PID_FILE.read_text().strip())
        try:
            os.kill(pid, 0)
            print(f"Dashboard already running (PID {pid}) at http://localhost:{port}")
            return
        except OSError:
            DASHBOARD_PID_FILE.unlink()

    dashboard_script = PACKAGE_ROOT / "dashboard.py"
    log_path = CUBICLE_HOME / "data" / "dashboard.log"

    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(dashboard_script),
         "--server.port", str(port), "--server.headless", "true"],
        stdout=open(log_path, "w"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    DASHBOARD_PID_FILE.write_text(str(proc.pid))
    print(f"Dashboard started (PID {proc.pid}) at http://localhost:{port}")
    print(f"Logs: {log_path}")


def stop_dashboard():
    if not DASHBOARD_PID_FILE.exists():
        print("No dashboard running.")
        return
    pid = int(DASHBOARD_PID_FILE.read_text().strip())
    try:
        os.kill(pid, signal.SIGTERM)
        DASHBOARD_PID_FILE.unlink()
        print(f"Dashboard stopped (PID {pid})")
    except OSError:
        DASHBOARD_PID_FILE.unlink()
        print("Dashboard was not running (stale PID removed).")


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if argv and argv[0] in LLM_WRAPPERS:
        agent_argv, observability = parse_wrapper_args(argv[1:])
        launch_agent(argv[0], agent_argv, observability=observability)
        return

    parser = argparse.ArgumentParser(
        description="Cubicle: A management tool for shared AI agent resources and telemetry.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Register hooks for a specific agent
  cubicle init-hooks --agent gemini

  # Remove hooks from an agent
  cubicle del-hooks --agent claude

  # Launch an agent through Cubicle and tag the process tree for telemetry
  cubicle claude --help
  cubicle gemini chat --model gemini-2.5-pro
  cubicle codex exec "fix the failing test"

  # Route agent model calls through a local MLflow gateway
  cubicle claude --observe
  cubicle gemini --observe
  cubicle codex --observe exec "fix the failing test"
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init hooks command
    init_parser = subparsers.add_parser(
        "init-hooks", 
        help="Initialize stable resources and register hooks",
        description="Ensures the ~/.cubicle hub is ready and registers absolute hook paths in agent settings."
    )
    init_parser.add_argument(
        "--agent",
        choices=["claude", "gemini", "codex", "copilot"],
        help="The AI agent family to register (claude, gemini, codex, or copilot)"
    )
    
    # Del hooks command
    del_parser = subparsers.add_parser(
        "del-hooks", 
        help="Unregister hooks from an agent",
        description="Removes the Cubicle telemetry hook entries from the specified agent's user settings."
    )
    del_parser.add_argument(
        "--agent", 
        required=True, 
        choices=["claude", "gemini", "codex", "copilot"],
        help="The AI agent family to unregister"
    )
    
    # Init command
    subparsers.add_parser(
        "init",
        help="Create ~/.cubicle/config.yaml with default event mappings",
        description="Creates ~/.cubicle/config.yaml if it doesn't exist, with default per-agent event mappings."
    )

    set_env_parser = subparsers.add_parser(
        "set-env",
        help="Set a shared env var for Cubicle-launched agents",
        description="Stores NAME=VALUE in ~/.cubicle/.env for Cubicle wrapper launches."
    )
    set_env_parser.add_argument("name", help="Environment variable name")
    set_env_parser.add_argument("value", help="Environment variable value")

    unset_env_parser = subparsers.add_parser(
        "unset-env",
        help="Remove a shared env var",
        description="Removes NAME from ~/.cubicle/.env if present."
    )
    unset_env_parser.add_argument("name", help="Environment variable name")

    subparsers.add_parser(
        "list-env",
        help="List shared env vars",
        description="Prints env vars stored in ~/.cubicle/.env."
    )

    # Dashboard commands
    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="Start the Cubicle telemetry dashboard in the background",
        description="Launches the Streamlit dashboard and runs it as a background process."
    )
    dashboard_parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_DASHBOARD_PORT,
        help=f"Port to run the dashboard on (default: {DEFAULT_DASHBOARD_PORT})"
    )

    subparsers.add_parser(
        "dashboard-stop",
        help="Stop the background dashboard process",
        description="Sends SIGTERM to the dashboard process and removes the PID file."
    )

    # Help command
    subparsers.add_parser("help", help="Show this help message")

    for agent in LLM_WRAPPERS:
        subparsers.add_parser(
            agent,
            add_help=False,
            help=f"Launch the upstream {agent} CLI with CUBICLE_LLM_FAMILY={agent}",
            description=f"Execs the upstream {agent} CLI and forwards all trailing arguments verbatim."
        )

    args = parser.parse_args(argv)

    if args.command == "init":
        init_config()
    elif args.command == "set-env":
        set_env_var(args.name, args.value)
    elif args.command == "unset-env":
        unset_env_var(args.name)
    elif args.command == "list-env":
        list_env_vars()
    elif args.command == "init-hooks":
        init_hooks(agent=args.agent)
    elif args.command == "del-hooks":
        del_hooks(args.agent)
    elif args.command == "dashboard":
        start_dashboard(port=args.port)
    elif args.command == "dashboard-stop":
        stop_dashboard()
    elif args.command == "help":
        parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
