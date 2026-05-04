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
def test_launch_agent_sets_family_and_forwards_args(monkeypatch, agent):
    captured = {}

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


def test_launch_agent_fails_when_executable_missing(monkeypatch, capsys):
    monkeypatch.setattr(cli.shutil, "which", lambda name: None)

    with pytest.raises(SystemExit) as excinfo:
        cli.launch_agent("claude", ["--help"])

    assert excinfo.value.code == 1
    assert "Could not find 'claude' on PATH" in capsys.readouterr().err
