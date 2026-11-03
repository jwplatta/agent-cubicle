"""Redact known secrets and common credential formats before durable storage."""

import os
import re
from urllib.parse import unquote, urlsplit

try:
    from pygarble.screening import Scanner
except ImportError:
    Scanner = None

SENSITIVE = re.compile(
    r"(?:password|passwd|secret|api[_-]?key|access[_-]?token|auth(?:orization)?|credential|"
    r"private[_-]?key|(?:^|[_-])(?:token|key)(?:$|[_-]))", re.I)
URL_CREDENTIAL = re.compile(r"(\b[a-z][a-z0-9+.-]*://[^\s:/@]+:)([^\s/@]+)(@)", re.I)
BEARER = re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+")


def known_secrets():
    values = set()
    for key, value in os.environ.items():
        if SENSITIVE.search(key) and len(value) >= 4:
            values.add(value)
        if "URL" in key and "://" in value:
            try:
                password = urlsplit(value).password
                if password and len(password) >= 4:
                    values.add(password)
                    values.add(unquote(password))
            except ValueError:
                continue
    return sorted(values, key=len, reverse=True)


def redact_text(value):
    for secret in known_secrets():
        value = value.replace(secret, "[REDACTED]")
    value = URL_CREDENTIAL.sub(r"\1[REDACTED]\3", value)
    value = BEARER.sub(r"\1[REDACTED]", value)
    if Scanner is not None:
        value = Scanner(categories=["secrets"], max_input_length=max(100000, len(value))).redact(value).text
    return value


def redact(value):
    if isinstance(value, dict):
        return {key: "[REDACTED]" if SENSITIVE.search(str(key)) and isinstance(item, str)
                else redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return redact_text(value) if isinstance(value, str) else value
