from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SEVERITY_ORDER = {"pass": 0, "info": 1, "warning": 2, "error": 3}


@dataclass(frozen=True)
class SourceFile:
    path: str
    text: str


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    title: str
    message: str
    remediation: str
    path: str | None = None
    line: int | None = None

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "remediation": self.remediation,
        }
        if self.path is not None:
            data["path"] = self.path
        if self.line is not None:
            data["line"] = self.line
        return data


@dataclass(frozen=True)
class RepositorySnapshot:
    root: Path
    files: tuple[SourceFile, ...]
    files_skipped: int


@dataclass(frozen=True)
class ScanReport:
    root: str
    files_scanned: int
    files_skipped: int
    findings: tuple[Finding, ...]

    @property
    def error_count(self) -> int:
        return sum(item.severity == "error" for item in self.findings)

    @property
    def warning_count(self) -> int:
        return sum(item.severity == "warning" for item in self.findings)

    @property
    def info_count(self) -> int:
        return sum(item.severity == "info" for item in self.findings)

    @property
    def ok(self) -> bool:
        return self.error_count == 0

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "ok": self.ok,
            "root": self.root,
            "files_scanned": self.files_scanned,
            "files_skipped": self.files_skipped,
            "summary": {
                "errors": self.error_count,
                "warnings": self.warning_count,
                "info": self.info_count,
            },
            "findings": [item.to_dict() for item in self.findings],
        }
