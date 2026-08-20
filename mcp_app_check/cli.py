from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .models import SEVERITY_ORDER, ScanReport
from .report import render_json, render_text
from .rules import scan_repository
from .sarif import render_sarif


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp-app-check",
        description="静态检查 MCP Apps 项目的协议就绪度和常见安全问题。",
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="要检查的项目目录，默认是当前目录。"
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "sarif"),
        default="text",
        help="输出格式。",
    )
    parser.add_argument("--output", "-o", type=Path, help="将报告写入文件。")
    parser.add_argument(
        "--fail-on",
        choices=("none", "warning", "error"),
        default="error",
        help="达到此严重级别时返回退出码 1；默认 error。",
    )
    parser.add_argument(
        "--include-passes", action="store_true", help="在文本报告中显示通过项。"
    )
    parser.add_argument(
        "--max-files", type=int, default=4_000, help="最多读取的源码文件数。"
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int,
        default=2_000_000,
        help="单个源码文件的最大字节数。",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = build_parser().parse_args(argv)
    try:
        report = scan_repository(
            Path(args.path),
            max_files=args.max_files,
            max_file_bytes=args.max_file_bytes,
        )
        if args.format == "json":
            output = render_json(report) + "\n"
        elif args.format == "sarif":
            output = render_sarif(report) + "\n"
        else:
            output = render_text(report, include_passes=args.include_passes)
        _write(output, args.output)
    except (OSError, ValueError) as exc:
        print(f"mcp-app-check: {exc}", file=sys.stderr)
        return 2
    return 1 if _fails(report, args.fail_on) else 0


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def _write(text: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(text)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8", newline="\n")


def _fails(report: ScanReport, threshold: str) -> bool:
    if threshold == "none":
        return False
    return any(
        item.severity != "pass"
        and SEVERITY_ORDER[item.severity] >= SEVERITY_ORDER[threshold]
        for item in report.findings
    )


if __name__ == "__main__":
    raise SystemExit(main())
