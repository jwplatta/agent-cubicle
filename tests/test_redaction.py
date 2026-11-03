import json
import os
import sys

from cubicle import redaction, worker


def test_redacts_known_secret_and_sensitive_fields(monkeypatch):
    monkeypatch.setenv("EXAMPLE_API_KEY", "synthetic-key-987654")
    result = redaction.redact({"message": "token synthetic-key-987654", "password": "hidden",
                               "input_tokens": 42})
    assert result == {"message": "token [REDACTED]", "password": "[REDACTED]",
                      "input_tokens": 42}


def test_worker_output_is_redacted_before_spooling(monkeypatch, tmp_path):
    monkeypatch.setenv("EXAMPLE_API_KEY", "synthetic-key-987654")
    script = ('import sys,json; print(json.dumps({"type":"result",'
              '"message":"synthetic-key-987654"}), flush=True); '
              'print("synthetic-key-987654",file=sys.stderr,flush=True)')
    assert worker.run_redacted([sys.executable, "-c", script], tmp_path, tmp_path,
                               dict(os.environ)) == 0
    out = (tmp_path / "stdout.jsonl").read_text()
    err = (tmp_path / "stderr.log").read_text()
    assert "synthetic-key-987654" not in out + err
    assert json.loads(out)["message"] == "[REDACTED]"
    assert (tmp_path / "stdout.jsonl").stat().st_mode & 0o777 == 0o600


def test_multiline_private_key_is_not_written_to_stderr(tmp_path):
    script = ('import sys; print("-----BEGIN PRIVATE KEY-----\\nsynthetic-private-material\\n"'
              '"-----END PRIVATE KEY-----", file=sys.stderr)')
    assert worker.run_redacted([sys.executable, "-c", script], tmp_path, tmp_path,
                               dict(os.environ)) == 0
    assert "synthetic-private-material" not in (tmp_path / "stderr.log").read_text()
