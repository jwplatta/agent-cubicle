"""Initialize Cubicle's local workspace and deploy versioned resources."""

import hashlib
import json
from pathlib import Path

import yaml

RESOURCE_DIR = Path(__file__).parent / "resources"
DIRECTORIES = ("backlog", "context", "logs", "runs", "artifacts", "resources")


def initialize(home: Path) -> Path:
    """Create missing resources without changing existing user configuration."""
    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    for name in DIRECTORIES:
        (home / name).mkdir(exist_ok=True, mode=0o700)
    config = home / "config.yaml"
    if not config.exists():
        try:
            with config.open("x") as stream:
                yaml.safe_dump({"supervisor": {"backend": "codex"}}, stream)
        except FileExistsError:
            pass

    source = RESOURCE_DIR / "supervisor.md"
    content = source.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    resource = home / "resources" / "supervisor" / digest / "supervisor.md"
    resource.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if resource.exists() and resource.read_bytes() != content:
        raise ValueError(f"Deployed resource differs from its content hash: {resource}")
    if not resource.exists():
        try:
            with resource.open("xb") as stream:
                stream.write(content)
        except FileExistsError:
            if resource.read_bytes() != content:
                raise ValueError(f"Deployed resource differs from its content hash: {resource}")
    manifest = resource.parent / "manifest.json"
    if not manifest.exists():
        try:
            with manifest.open("x") as stream:
                json.dump({"source": "supervisor.md", "sha256": digest}, stream, indent=2)
                stream.write("\n")
        except FileExistsError:
            pass
    return resource


def supervisor_backend(home: Path) -> str:
    config = home / "config.yaml"
    if not config.exists():
        return "codex"
    with config.open() as stream:
        data = yaml.safe_load(stream) or {}
    if not isinstance(data, dict) or not isinstance(data.get("supervisor", {}), dict):
        raise ValueError("Invalid supervisor configuration in config.yaml")
    backend = data.get("supervisor", {}).get("backend", "codex")
    if not isinstance(backend, str):
        raise ValueError("Supervisor backend must be a string")
    return backend
