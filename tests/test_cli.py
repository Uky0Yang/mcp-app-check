from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from mcp_app_check.cli import main
from tests.fixtures import READY_APP


class CliTests(unittest.TestCase):
    def test_json_report_is_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "server.ts").write_text(READY_APP, encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main([str(root), "--format", "json"])

            payload = json.loads(stdout.getvalue())
            self.assertEqual(0, code)
            self.assertTrue(payload["ok"])
            self.assertEqual("1.0", payload["schema_version"])
            self.assertEqual(0, payload["summary"]["errors"])

    def test_default_threshold_fails_on_errors(self) -> None:
        with (
            tempfile.TemporaryDirectory() as directory,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            code = main([directory])

        self.assertEqual(1, code)

    def test_fail_on_warning_is_stricter(self) -> None:
        minimal = """
const uri = "ui://demo/app.html";
const mimeType = "text/html;profile=mcp-app";
const tool = { resourceUri: uri, content: [{ type: "text", text: "ok" }] };
""".strip()
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "server.ts").write_text(minimal, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code = main([directory, "--fail-on", "warning"])

        self.assertEqual(1, code)

    def test_output_file_is_written(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "server.ts").write_text(READY_APP, encoding="utf-8")
            output = root / "reports" / "mcp-app-check.json"

            code = main([str(root), "--format", "json", "--output", str(output)])

            self.assertEqual(0, code)
            self.assertTrue(json.loads(output.read_text(encoding="utf-8"))["ok"])

    def test_missing_path_returns_usage_error(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main(["definitely-missing-path"])

        self.assertEqual(2, code)
        self.assertIn("does not exist", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
