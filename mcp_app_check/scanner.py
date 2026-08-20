from __future__ import annotations

import os
from pathlib import Path

from .models import RepositorySnapshot, SourceFile

IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "venv",
}

SOURCE_SUFFIXES = {
    ".cjs",
    ".cs",
    ".go",
    ".htm",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".mjs",
    ".py",
    ".rs",
    ".svelte",
    ".toml",
    ".ts",
    ".tsx",
    ".vue",
    ".yaml",
    ".yml",
}


def collect_sources(
    root: Path,
    *,
    max_files: int = 4_000,
    max_file_bytes: int = 2_000_000,
) -> RepositorySnapshot:
    root = root.resolve()
    if not root.exists():
        raise ValueError(f"path does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"path is not a directory: {root}")
    if max_files < 1:
        raise ValueError("max_files must be at least 1")
    if max_file_bytes < 1:
        raise ValueError("max_file_bytes must be at least 1")

    sources: list[SourceFile] = []
    skipped = 0
    candidates_seen = 0

    for current_root, directories, filenames in os.walk(root, followlinks=False):
        current = Path(current_root)
        directories[:] = sorted(
            name
            for name in directories
            if name not in IGNORED_DIRECTORIES and not (current / name).is_symlink()
        )
        for filename in sorted(filenames):
            full_path = current / filename
            if (
                full_path.suffix.lower() not in SOURCE_SUFFIXES
                or full_path.is_symlink()
            ):
                continue
            if candidates_seen >= max_files:
                skipped += 1
                continue
            candidates_seen += 1
            try:
                if full_path.stat().st_size > max_file_bytes:
                    skipped += 1
                    continue
                text = full_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                skipped += 1
                continue
            sources.append(SourceFile(full_path.relative_to(root).as_posix(), text))

    return RepositorySnapshot(root=root, files=tuple(sources), files_skipped=skipped)
