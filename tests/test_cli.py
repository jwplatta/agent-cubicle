import pytest

from cubicle import cli


def test_codex_hook_registration_preserves_unrelated_settings(tmp_path):
    import tomllib

    path = tmp_path / "config.toml"
    path.write_text('''# Keep this comment
model = "example"
[features]
other = true
[[hooks.PreToolUse]]
matcher = "*"
[[hooks.PreToolUse.hooks]]
name = "other-hook"
type = "command"
command = "echo keep"
[mcp_servers.example]
command = "example"
''')
    cli.update_codex_toml(path, "/tmp/cubicle-hook.py", ["PreToolUse", "Stop"])
    cli.update_codex_toml(path, "/tmp/cubicle-hook.py", ["PreToolUse", "Stop"])
    data = tomllib.loads(path.read_text())
    assert data["mcp_servers"]["example"]["command"] == "example"
    assert data["features"]["other"] is True
    assert sum(h["name"] == "cubicle-telemetry" for group in data["hooks"]["PreToolUse"]
               for h in group["hooks"]) == 1
    assert "# Keep this comment" in path.read_text()
    cli.remove_codex_toml(path, "/tmp/cubicle-hook.py")
    data = tomllib.loads(path.read_text())
    assert data["hooks"]["PreToolUse"][0]["hooks"][0]["name"] == "other-hook"
    assert data["mcp_servers"]["example"]["command"] == "example"


def test_main_dispatches_claude_wrapper(monkeypatch):
    calls = []

    def fake_launch(agent, argv):
        calls.append((agent, argv))

    monkeypatch.setattr(cli, "launch_agent", fake_launch)

    cli.main(["claude", "--help"])

    assert calls == [("claude", ["--help"])]


@pytest.mark.parametrize("agent", ["claude", "agy", "codex"])
def test_launch_agent_sets_family_and_forwards_args(monkeypatch, agent, tmp_path):
    captured = {}

    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setattr(cli.shutil, "which", lambda name: f"/usr/local/bin/{name}")

    def fake_execvpe(path, argv, env):
        captured["path"] = path
        captured["argv"] = argv
        captured["env"] = env
        raise SystemExit(0)

    monkeypatch.setattr(cli.os, "execvpe", fake_execvpe)
    monkeypatch.setenv("UNCHANGED_VAR", "present")

    with pytest.raises(SystemExit) as excinfo:
        cli.launch_agent(agent, ["chat", "--flag"])

    assert excinfo.value.code == 0
    assert captured["path"] == f"/usr/local/bin/{agent}"
    assert captured["argv"] == [agent, "chat", "--flag"]
    assert captured["env"]["CUBICLE_LLM_FAMILY"] == agent
    assert captured["env"]["UNCHANGED_VAR"] == "present"


def test_launch_agent_loads_shared_env_and_overrides_process_env(monkeypatch, tmp_path):
    captured = {}
    env_file = tmp_path / ".env"
    env_file.write_text('SHARED_TOKEN="from-file"\nUNCHANGED_VAR="override"\n')

    monkeypatch.setattr(cli, "ENV_FILE", env_file)
    monkeypatch.setattr(cli.shutil, "which", lambda name: f"/usr/local/bin/{name}")

    def fake_execvpe(path, argv, env):
        captured["env"] = env
        raise SystemExit(0)

    monkeypatch.setattr(cli.os, "execvpe", fake_execvpe)
    monkeypatch.setenv("UNCHANGED_VAR", "from-shell")

    with pytest.raises(SystemExit):
        cli.launch_agent("codex", ["exec", "status"])

    assert captured["env"]["SHARED_TOKEN"] == "from-file"
    assert captured["env"]["UNCHANGED_VAR"] == "override"



def test_launch_agent_fails_when_executable_missing(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setattr(cli.shutil, "which", lambda name: None)

    with pytest.raises(SystemExit) as excinfo:
        cli.launch_agent("claude", ["--help"])

    assert excinfo.value.code == 1
    assert "Could not find 'claude' on PATH" in capsys.readouterr().err


def test_set_env_creates_file_and_updates_existing_key(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "CUBICLE_HOME", tmp_path)
    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / ".env")

    cli.main(["set-env", "API_KEY", "first"])
    cli.main(["set-env", "API_KEY", "second"])
    cli.main(["set-env", "GREETING", "hello world"])

    assert (tmp_path / ".env").read_text() == 'API_KEY="second"\nGREETING="hello world"\n'
    assert "Set API_KEY" in capsys.readouterr().out


def test_unset_env_removes_key_and_is_noop_if_missing(monkeypatch, tmp_path, capsys):
    env_file = tmp_path / ".env"
    env_file.write_text('API_KEY="secret"\nKEEP_ME="yes"\n')
    monkeypatch.setattr(cli, "CUBICLE_HOME", tmp_path)
    monkeypatch.setattr(cli, "ENV_FILE", env_file)

    cli.main(["unset-env", "API_KEY"])
    assert env_file.read_text() == 'KEEP_ME="yes"\n'

    cli.main(["unset-env", "DOES_NOT_EXIST"])
    assert env_file.read_text() == 'KEEP_ME="yes"\n'
    assert "Removed API_KEY" in capsys.readouterr().out


def test_list_env_prints_current_entries(monkeypatch, tmp_path, capsys):
    env_file = tmp_path / ".env"
    env_file.write_text('API_KEY="secret"\nGREETING="hello world"\n')
    monkeypatch.setattr(cli, "ENV_FILE", env_file)

    cli.main(["list-env"])

    assert capsys.readouterr().out == "API_KEY=secret\nGREETING=hello world\n"


def test_set_env_rejects_invalid_name(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "CUBICLE_HOME", tmp_path)
    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / ".env")

    with pytest.raises(SystemExit) as excinfo:
        cli.main(["set-env", "BAD-NAME", "value"])

    assert excinfo.value.code == 1
    assert "Invalid environment variable name: BAD-NAME" in capsys.readouterr().err


def test_init_preserves_config_and_deploys_versioned_prompt(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "CUBICLE_HOME", tmp_path)
    config = tmp_path / "config.yaml"
    config.write_text("custom: existing\n")
    cli.main(["init"])
    cli.main(["init"])
    assert config.read_text() == "custom: existing\n"
    assert (tmp_path / "backlog").is_dir()
    prompts = list((tmp_path / "resources" / "supervisor").glob("*/supervisor.md"))
    assert len(prompts) == 1
    assert (prompts[0].parent / "manifest.json").exists()


def test_supervisor_uses_config_and_explicit_override(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "CUBICLE_HOME", tmp_path)
    (tmp_path / "config.yaml").write_text("supervisor:\n  backend: claude\n")
    calls = []
    monkeypatch.setattr(cli, "launch_agent", lambda agent, argv: calls.append((agent, argv)))
    cli.main(["supervisor"])
    cli.main(["supervisor", "--backend", "codex"])
    assert [call[0] for call in calls] == ["claude", "codex"]
    assert all("supervisor.md" in call[1][-1] for call in calls)


def test_supervisor_defaults_to_codex_and_rejects_invalid_config(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "CUBICLE_HOME", tmp_path)
    calls = []
    monkeypatch.setattr(cli, "launch_agent", lambda agent, argv: calls.append((agent, argv)))
    cli.main(["supervisor"])
    assert calls[0][0] == "codex"
    (tmp_path / "config.yaml").write_text("supervisor:\n  backend: []\n")
    with pytest.raises(SystemExit):
        cli.main(["supervisor"])
    assert "backend must be a string" in capsys.readouterr().err


def test_init_new_config_keeps_legacy_hook_mappings(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "CUBICLE_HOME", tmp_path)
    cli.main(["init"])
    config = cli.yaml.safe_load((tmp_path / "config.yaml").read_text())
    assert config["supervisor"]["backend"] == "codex"
    assert "codex" in config["agents"]


def test_supervisor_forwards_optional_initial_message(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "CUBICLE_HOME", tmp_path)
    calls = []
    monkeypatch.setattr(cli, "launch_agent", lambda agent, argv: calls.append((agent, argv)))
    cli.main(["supervisor", "Plan my tasks"])
    assert "User request: Plan my tasks" in calls[0][1][-1]


def test_shared_env_is_private(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "CUBICLE_HOME", tmp_path)
    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / ".env")
    cli.main(["set-env", "TEST_SECRET", "value"])
    assert (tmp_path / ".env").stat().st_mode & 0o777 == 0o600
