"""Simple dispatch check for quota data captured from the agy status line."""

import json
import math
import os
import select
import subprocess
import time
from pathlib import Path

import yaml


def codex_limits(timeout=10):
    """Read the same account windows displayed by Codex, without consuming credits."""
    proc = subprocess.Popen(["codex", "app-server"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    deadline = time.monotonic() + timeout
    buffer = b""

    def send(value):
        proc.stdin.write((json.dumps(value) + "\n").encode())
        proc.stdin.flush()

    def receive(request_id):
        nonlocal buffer
        while time.monotonic() < deadline:
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                try:
                    response = json.loads(line)
                except ValueError:
                    continue
                if response.get("id") == request_id:
                    if "error" in response or not isinstance(response.get("result"), dict):
                        raise ValueError("Codex usage request failed")
                    return response["result"]
            if not select.select([proc.stdout], [], [], max(0, deadline - time.monotonic()))[0]:
                break
            chunk = os.read(proc.stdout.fileno(), 65536)
            if not chunk:
                break
            buffer += chunk
        raise ValueError("Codex usage request timed out or closed")

    try:
        send({"id": 1, "method": "initialize", "params": {
            "clientInfo": {"name": "cubicle", "version": "0.1"}}})
        receive(1)
        send({"method": "initialized", "params": {}})
        send({"id": 2, "method": "account/rateLimits/read"})
        return receive(2)
    except (OSError, BrokenPipeError) as exc:
        raise ValueError("Codex usage unavailable") from exc
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        proc.stdin.close()
        proc.stdout.close()


def check_codex(home):
    config = Path(home) / "config.yaml"
    data = yaml.safe_load(config.read_text()) if config.exists() else {}
    threshold = (data or {}).get("limits", {}).get("codex_max_used_percent", 80)
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not 0 < threshold <= 100:
        raise ValueError("limits.codex_max_used_percent must be between 0 and 100")
    try:
        result = codex_limits()
        buckets = result.get("rateLimitsByLimitId") or ({"codex": result["rateLimits"]}
                    if result.get("rateLimits") else {})
        windows = [bucket.get(name) for bucket in buckets.values() if isinstance(bucket, dict)
                   for name in ("primary", "secondary") if bucket.get(name) is not None]
        values = [window.get("usedPercent") for window in windows if isinstance(window, dict)]
        if not values or len(values) != len(windows) or any(
            isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
            or v < 0 for v in values
        ):
            raise ValueError("No usable Codex account usage data")
    except (OSError, TypeError, KeyError, ValueError) as exc:
        raise ValueError("Codex usage unavailable; dispatch paused") from exc
    if any(value >= threshold for value in values):
        raise ValueError("Codex usage limit reached; dispatch paused")
    return {"max_used_percent": max(values), "threshold": threshold}


def check_agy(home):
    home = Path(home)
    config = home / "config.yaml"
    data = yaml.safe_load(config.read_text()) if config.exists() else {}
    limits = (data or {}).get("limits", {})
    threshold = limits.get("agy_max_used_percent", 80)
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not 0 < threshold <= 100:
        raise ValueError("limits.agy_max_used_percent must be between 0 and 100")
    snapshot = home / "usage" / "agy.json"
    try:
        saved = json.loads(snapshot.read_text())
        age = time.time() - saved["observed_at"]
        fractions = saved["remaining_fractions"]
        if not 0 <= age <= 300 or not isinstance(fractions, dict) or not fractions:
            raise ValueError("stale or empty")
        valid = [v for v in fractions.values() if isinstance(v, (int, float))
                 and not isinstance(v, bool) and 0 <= v <= 1]
        if len(valid) != len(fractions):
            raise ValueError("invalid fractions")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Antigravity usage unavailable or stale; start an agy supervisor "
                         "and refresh its quota before dispatch") from exc
    if any((1 - fraction) * 100 >= threshold for fraction in valid):
        raise ValueError("Antigravity usage limit reached; dispatch paused")
