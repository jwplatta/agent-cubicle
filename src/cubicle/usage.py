"""Simple dispatch check for quota data captured from the agy status line."""

import json
import time
from pathlib import Path

import yaml


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
