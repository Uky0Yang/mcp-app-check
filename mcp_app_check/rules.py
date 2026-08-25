from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .models import SEVERITY_ORDER, Finding, RepositorySnapshot, ScanReport, SourceFile
from .scanner import collect_sources


@dataclass(frozen=True)
class Rule:
    rule_id: str
    severity: str
    title: str
    remediation: str


RULES = {
    "MCA001": Rule(
        "MCA001",
        "error",
        "缺少 ui:// 资源",
        "声明至少一个使用 ui:// URI 的 MCP App 资源。",
    ),
    "MCA002": Rule(
        "MCA002",
        "error",
        "缺少 MCP App MIME",
        "为 UI 资源返回 text/html;profile=mcp-app。",
    ),
    "MCA003": Rule(
        "MCA003",
        "error",
        "工具未关联 UI",
        "在工具元数据中用 resourceUri 或 resource_uri 关联 ui:// 资源。",
    ),
    "MCA004": Rule(
        "MCA004",
        "warning",
        "缺少 structuredContent",
        "让工具返回 structuredContent，供 UI 稳定读取结构化数据。",
    ),
    "MCA005": Rule(
        "MCA005",
        "warning",
        "缺少文本降级结果",
        "同时返回 content 文本，使不支持 MCP Apps 的客户端仍能完成任务。",
    ),
    "MCA006": Rule(
        "MCA006",
        "warning",
        "敏感浏览器权限需要复核",
        "仅声明业务确实需要的权限，并在项目文档中解释用途。",
    ),
    "MCA007": Rule(
        "MCA007",
        "warning",
        "外部来源缺少 CSP 声明",
        "在 UI 资源元数据中显式声明 csp 的 connect/resource domains。",
    ),
    "MCA008": Rule(
        "MCA008", "error", "CSP 域允许通配符", "把通配符替换为实际需要的最小来源列表。"
    ),
    "MCA009": Rule(
        "MCA009", "error", "疑似提交了密钥", "删除疑似密钥；若值真实存在，请立即轮换。"
    ),
}

UI_URI = re.compile(r"ui://[A-Za-z0-9._~!$&'()*+,;=:@/?%\-]+")
MCP_APP_MIME = re.compile(r"text/html\s*;\s*profile=mcp-app", re.IGNORECASE)
OFFICIAL_MIME_IMPORT = re.compile(
    r"\bimport\s*\{[^}]*\bRESOURCE_MIME_TYPE\b[^}]*\}\s*from\s*"
    r"(['\"])@modelcontextprotocol/ext-apps/server\1",
    re.DOTALL,
)
OFFICIAL_RESOURCE_HELPER_IMPORT = re.compile(
    r"\bimport\s*\{[^}]*\bregisterAppResource\b[^}]*\}\s*from\s*"
    r"(['\"])@modelcontextprotocol/ext-apps/server\1",
    re.DOTALL,
)
REGISTER_APP_RESOURCE_CALL = re.compile(r"\bregisterAppResource\s*\(")
MIME_CONSTANT_USE = re.compile(
    r"\b(?:mimeType|mime_type)\b\s*[:=]\s*RESOURCE_MIME_TYPE\b"
)
RESOURCE_URI_FIELD = re.compile(r"\b(?:resourceUri|resource_uri)\b")
STRUCTURED_CONTENT = re.compile(r"\b(?:structuredContent|structured_content)\b")
CONTENT_FIELD = re.compile(r"\bcontent\s*[:=]\s*\[")
TEXT_FIELD = re.compile(r"\btext\s*[:=]")
MCP_TYPES_IMPORT = re.compile(r"\bfrom\s+mcp\s+import\s+types\b")
MCP_TYPES_TEXT_CONTENT = re.compile(r"\btypes\.TextContent\s*\(")
MCP_TEXT_CONTENT_IMPORT = re.compile(
    r"\bfrom\s+mcp\.types\s+import\s+[^\n]*\bTextContent\b"
)
MCP_TEXT_CONTENT = re.compile(r"(?<!\.)\bTextContent\s*\(")
SENSITIVE_PERMISSIONS = re.compile(
    r"\bpermissions\b\s*[:=]\s*\{.{0,500}?\b(?:camera|microphone|geolocation|clipboardWrite|clipboard_write)\b\s*[:=]",
    re.DOTALL,
)
EXTERNAL_URL = re.compile(
    r"https://(?!localhost\b|127\.0\.0\.1\b)[A-Za-z0-9.-]+", re.IGNORECASE
)
CSP_FIELD = re.compile(
    r"\b(?:csp|connectDomains|resourceDomains|connect_domains|resource_domains)\b"
)
WILDCARD_CSP = re.compile(
    r"\b(?:connectDomains|resourceDomains|connect_domains|resource_domains)\b\s*[:=].{0,240}?(['\"])\*\1",
    re.DOTALL,
)
SECRET_PATTERNS = (
    re.compile(r"\bgh[opusr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
)

WEB_SOURCE_SUFFIXES = (
    ".html",
    ".htm",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".vue",
    ".svelte",
)


def scan_repository(
    root: Path,
    *,
    max_files: int = 4_000,
    max_file_bytes: int = 2_000_000,
) -> ScanReport:
    snapshot = collect_sources(root, max_files=max_files, max_file_bytes=max_file_bytes)
    findings = run_checks(snapshot)
    findings.sort(
        key=lambda item: (
            -SEVERITY_ORDER[item.severity],
            item.rule_id,
            item.path or "",
            item.line or 0,
        )
    )
    return ScanReport(
        root=str(snapshot.root),
        files_scanned=len(snapshot.files),
        files_skipped=snapshot.files_skipped,
        findings=tuple(findings),
    )


def run_checks(snapshot: RepositorySnapshot) -> list[Finding]:
    findings = [
        _required_signal(snapshot, "MCA001", UI_URI, "已检测到 ui:// UI 资源。"),
        _mcp_app_mime(snapshot),
        _tool_binding(snapshot),
        _recommended_signal(
            snapshot, "MCA004", STRUCTURED_CONTENT, "已检测到 structuredContent。"
        ),
        _text_fallback(snapshot),
        _forbidden_pattern(
            snapshot,
            "MCA006",
            SENSITIVE_PERMISSIONS,
            "检测到 camera、microphone、geolocation 或 clipboard 权限声明。",
        ),
        _csp_check(snapshot),
        _forbidden_pattern(snapshot, "MCA008", WILDCARD_CSP, "CSP 域列表包含 '*'。"),
        _secret_check(snapshot),
    ]
    return findings


def _required_signal(
    snapshot: RepositorySnapshot,
    rule_id: str,
    pattern: re.Pattern[str],
    pass_message: str,
) -> Finding:
    match = _first_match(snapshot.files, pattern)
    if match is not None:
        source, found = match
        return _finding(rule_id, "pass", pass_message, source, found)
    return _finding(rule_id, RULES[rule_id].severity, RULES[rule_id].title)


def _recommended_signal(
    snapshot: RepositorySnapshot,
    rule_id: str,
    pattern: re.Pattern[str],
    pass_message: str,
) -> Finding:
    match = _first_match(snapshot.files, pattern)
    if match is not None:
        source, found = match
        return _finding(rule_id, "pass", pass_message, source, found)
    return _finding(rule_id, RULES[rule_id].severity, RULES[rule_id].title)


def _mcp_app_mime(snapshot: RepositorySnapshot) -> Finding:
    literal_match = _first_match(snapshot.files, MCP_APP_MIME)
    if literal_match is not None:
        source, found = literal_match
        return _finding("MCA002", "pass", "已检测到 MCP App HTML MIME。", source, found)
    import_match = _first_match(snapshot.files, OFFICIAL_MIME_IMPORT)
    if import_match is not None:
        source, found = import_match
        if MIME_CONSTANT_USE.search(source.text):
            return _finding(
                "MCA002",
                "pass",
                "已检测到官方 MCP Apps MIME constant。",
                source,
                found,
            )
    for source in snapshot.files:
        helper_import = OFFICIAL_RESOURCE_HELPER_IMPORT.search(source.text)
        if helper_import is not None and REGISTER_APP_RESOURCE_CALL.search(source.text):
            return _finding(
                "MCA002",
                "pass",
                "已检测到使用默认 MCP App MIME 的官方 resource helper。",
                source,
                helper_import,
            )
    return _finding("MCA002", RULES["MCA002"].severity, RULES["MCA002"].title)


def _tool_binding(snapshot: RepositorySnapshot) -> Finding:
    ui_match = _first_match(snapshot.files, UI_URI)
    field_match = _first_match(snapshot.files, RESOURCE_URI_FIELD)
    if ui_match is not None and field_match is not None:
        source, found = field_match
        return _finding(
            "MCA003", "pass", "已检测到工具与 UI 资源的关联。", source, found
        )
    return _finding("MCA003", RULES["MCA003"].severity, RULES["MCA003"].title)


def _text_fallback(snapshot: RepositorySnapshot) -> Finding:
    for source in snapshot.files:
        text_content = MCP_TYPES_TEXT_CONTENT.search(source.text)
        if text_content is not None and MCP_TYPES_IMPORT.search(source.text):
            return _finding(
                "MCA005",
                "pass",
                "已检测到 FastMCP TextContent 文本降级结果。",
                source,
                text_content,
            )
        text_content = MCP_TEXT_CONTENT.search(source.text)
        if text_content is not None and MCP_TEXT_CONTENT_IMPORT.search(source.text):
            return _finding(
                "MCA005",
                "pass",
                "已检测到 FastMCP TextContent 文本降级结果。",
                source,
                text_content,
            )
    content_match = _first_match(snapshot.files, CONTENT_FIELD)
    text_match = _first_match(snapshot.files, TEXT_FIELD)
    if content_match is not None and text_match is not None:
        source, found = content_match
        return _finding("MCA005", "pass", "已检测到文本降级结果。", source, found)
    return _finding("MCA005", RULES["MCA005"].severity, RULES["MCA005"].title)


def _forbidden_pattern(
    snapshot: RepositorySnapshot,
    rule_id: str,
    pattern: re.Pattern[str],
    message: str,
) -> Finding:
    match = _first_match(snapshot.files, pattern)
    if match is None:
        return _finding(rule_id, "pass", f"未发现：{RULES[rule_id].title}。")
    source, found = match
    return _finding(rule_id, RULES[rule_id].severity, message, source, found)


def _csp_check(snapshot: RepositorySnapshot) -> Finding:
    web_sources = tuple(
        source
        for source in snapshot.files
        if source.path.lower().endswith(WEB_SOURCE_SUFFIXES)
    )
    external_match = _first_match(web_sources, EXTERNAL_URL)
    if external_match is None:
        return _finding("MCA007", "pass", "未检测到需要声明的外部 HTTPS 来源。")
    if _first_match(snapshot.files, CSP_FIELD) is not None:
        source, found = external_match
        return _finding(
            "MCA007", "pass", "已检测到外部来源和 CSP 声明。", source, found
        )
    source, found = external_match
    return _finding(
        "MCA007", RULES["MCA007"].severity, RULES["MCA007"].title, source, found
    )


def _secret_check(snapshot: RepositorySnapshot) -> Finding:
    for pattern in SECRET_PATTERNS:
        match = _first_match(snapshot.files, pattern)
        if match is not None:
            source, found = match
            return _finding(
                "MCA009", RULES["MCA009"].severity, RULES["MCA009"].title, source, found
            )
    return _finding("MCA009", "pass", "未检测到常见密钥格式。")


def _first_match(
    files: tuple[SourceFile, ...], pattern: re.Pattern[str]
) -> tuple[SourceFile, re.Match[str]] | None:
    for source in files:
        match = pattern.search(source.text)
        if match is not None:
            return source, match
    return None


def _finding(
    rule_id: str,
    severity: str,
    message: str,
    source: SourceFile | None = None,
    match: re.Match[str] | None = None,
) -> Finding:
    rule = RULES[rule_id]
    return Finding(
        rule_id=rule_id,
        severity=severity,
        title=rule.title,
        message=message,
        remediation=rule.remediation,
        path=source.path if source else None,
        line=_line_number(source.text, match.start()) if source and match else None,
    )


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1
