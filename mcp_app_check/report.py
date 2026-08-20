from __future__ import annotations

import json

from .models import ScanReport

SEVERITY_LABELS = {
    "error": "错误",
    "warning": "警告",
    "info": "提示",
    "pass": "通过",
}


def render_json(report: ScanReport) -> str:
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)


def render_text(report: ScanReport, *, include_passes: bool = False) -> str:
    lines = [
        f"mcp-app-check 已扫描 {report.files_scanned} 个文件：{report.root}",
        f"errors={report.error_count} warnings={report.warning_count} info={report.info_count} skipped={report.files_skipped}",
    ]
    visible = [
        item for item in report.findings if include_passes or item.severity != "pass"
    ]
    if not visible:
        lines.append("\n未发现阻塞项或警告。静态检查不等同于完整协议一致性测试。")
        return "\n".join(lines) + "\n"

    lines.append("")
    for item in visible:
        location = ""
        if item.path:
            location = f" {item.path}"
            if item.line:
                location += f":{item.line}"
        lines.append(
            f"[{SEVERITY_LABELS[item.severity]}] {item.rule_id}{location} {item.message}"
        )
        if item.severity != "pass":
            lines.append(f"  修复：{item.remediation}")
    return "\n".join(lines) + "\n"
