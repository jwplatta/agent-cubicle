import pytest

from cubicle import cli


def test_main_dispatches_claude_wrapper(monkeypatch):
    calls = []

    def fake_launch(agent, argv):
        calls.append((agent, argv))

    monkeypatch.setattr(cli, "launch_agent", fake_launch)

    cli.main(["claude", "--help"])

    assert calls == [("claude", ["--help"])]


@pytest.mark.parametrize("agent", ["claude", "gemini", "codex"])
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
