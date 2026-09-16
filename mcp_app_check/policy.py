"""Explicit JSON policies. Target repositories cannot configure their own scan."""

import json
from pathlib import Path

from .rules import RULES


def load_policy(path: Path | None, cli_ignore: list[str], fail_on: str | None):
    data = json.loads(path.read_text(encoding="utf-8")) if path else {}
    if not isinstance(data, dict) or set(data) - {"ignore", "fail_on"}:
        raise ValueError("policy must be an object with only ignore and fail_on")
    ignored = data.get("ignore", [])
    if not isinstance(ignored, list) or any(
        not isinstance(rule, str) for rule in ignored
    ):
        raise ValueError("ignore must be a list of rule IDs")
    configured_threshold = data.get("fail_on", "error")
    if configured_threshold not in ("none", "warning", "error"):
        raise ValueError("fail_on must be none, warning, or error")
    ignored = set(ignored) | set(cli_ignore)
    if ignored - set(RULES):
        raise ValueError("unknown rule IDs: " + ", ".join(sorted(ignored - set(RULES))))
    return ignored, fail_on or configured_threshold
