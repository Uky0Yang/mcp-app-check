from __future__ import annotations

import json

from . import __version__
from .models import Finding, ScanReport
from .rules import RULES, Rule

SARIF_LEVELS = {
    "error": "error",
    "warning": "warning",
    "info": "note",
}


def render_sarif(report: ScanReport) -> str:
    payload = {
        "$schema": "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "properties": {"findingsSuppressed": report.findings_suppressed},
                "tool": {
                    "driver": {
                        "name": "mcp-app-check",
                        "semanticVersion": __version__,
                        "informationUri": "https://github.com/Uky0Yang/mcp-app-check",
                        "rules": [_rule_descriptor(rule) for rule in RULES.values()],
                    }
                },
                "results": [
                    _result(finding)
                    for finding in report.findings
                    if finding.severity != "pass"
                ],
            }
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _rule_descriptor(rule: Rule) -> dict[str, object]:
    return {
        "id": rule.rule_id,
        "name": rule.title,
        "shortDescription": {"text": rule.title},
        "help": {"text": rule.remediation},
        "helpUri": "https://github.com/Uky0Yang/mcp-app-check#当前规则",
        "defaultConfiguration": {"level": SARIF_LEVELS[rule.severity]},
    }


def _result(finding: Finding) -> dict[str, object]:
    result: dict[str, object] = {
        "ruleId": finding.rule_id,
        "level": SARIF_LEVELS[finding.severity],
        "message": {"text": finding.message},
        "properties": {"remediation": finding.remediation},
    }
    if finding.path is not None:
        physical_location: dict[str, object] = {
            "artifactLocation": {"uri": finding.path},
        }
        if finding.line is not None:
            physical_location["region"] = {"startLine": finding.line}
        result["locations"] = [{"physicalLocation": physical_location}]
    return result
