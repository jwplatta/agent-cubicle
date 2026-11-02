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
                defaults = yaml.safe_load((RESOURCE_DIR.parent / "default_config.yaml").read_text())
                defaults["supervisor"] = {"backend": "codex"}
                yaml.safe_dump(defaults, stream, sort_keys=False)
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
    for name in ("cubicle-supervisor", "cubicle-worker"):
        skill_content = (RESOURCE_DIR / name / "SKILL.md").read_bytes()
        skill_hash = hashlib.sha256(skill_content).hexdigest()
        skill = home / "resources" / "skills" / name / skill_hash / "SKILL.md"
        skill.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if skill.exists() and skill.read_bytes() != skill_content:
            raise ValueError(f"Deployed skill differs from its content hash: {skill}")
        if not skill.exists():
            try:
                with skill.open("xb") as stream:
                    stream.write(skill_content)
            except FileExistsError:
                if skill.read_bytes() != skill_content:
                    raise ValueError(f"Deployed skill differs from its content hash: {skill}")
    return resource


def skill_path(home: Path, name: str) -> Path:
    if name not in {"cubicle-supervisor", "cubicle-worker"}:
        raise ValueError("Unknown Cubicle skill")
    content = (RESOURCE_DIR / name / "SKILL.md").read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    return home / "resources" / "skills" / name / digest / "SKILL.md"


def supervisor_skill_path(home: Path) -> Path:
    return skill_path(home, "cubicle-supervisor")


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
