# Agent Instructions

## Purpose

This repository is a dependency-free, read-only static checker for MCP Apps projects. Keep changes small, deterministic, and compatible with Python 3.10+.

## Boundaries

- Never execute target repository code, install its dependencies, start its MCP server, call a model, or make network requests during a scan.
- Do not follow directory symlinks.
- Treat stable MCP Apps specification requirements separately from optional guidance and draft behavior.
- Preserve stable rule IDs. A rule needs positive and negative tests, actionable remediation, and README documentation.
- Avoid broad regex rules that cannot be bounded well enough to keep false positives understandable.

## Verification

Run:

```powershell
python -m unittest discover -s tests -t . -v
python -m compileall -q mcp_app_check tests
python -m mcp_app_check examples\ready-app --fail-on warning
```
