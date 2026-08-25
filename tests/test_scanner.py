from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from mcp_app_check.rules import scan_repository
from tests.fixtures import (
    OFFICIAL_TYPESCRIPT_DEFAULT_MIME_APP,
    OFFICIAL_TYPESCRIPT_HELPERS_APP,
    OFFICIAL_TYPESCRIPT_UNUSED_MIME_IMPORT_APP,
    READY_APP,
)


class ScannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, relative_path: str, content: str) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def report(self):
        return scan_repository(self.root)

    def active_rules(self) -> set[str]:
        return {
            item.rule_id for item in self.report().findings if item.severity != "pass"
        }

    def test_ready_typescript_app_has_no_errors_or_warnings(self) -> None:
        self.write("src/server.ts", READY_APP)

        report = self.report()

        self.assertEqual(0, report.error_count)
        self.assertEqual(0, report.warning_count)
        self.assertTrue(report.ok)
        self.assertEqual(1, report.files_scanned)

    def test_official_typescript_mime_constant_is_recognized(self) -> None:
        self.write("src/server.ts", OFFICIAL_TYPESCRIPT_HELPERS_APP)

        self.assertNotIn("MCA002", self.active_rules())

    def test_official_typescript_resource_helper_default_mime_is_recognized(
        self,
    ) -> None:
        self.write("src/server.ts", OFFICIAL_TYPESCRIPT_DEFAULT_MIME_APP)

        self.assertNotIn("MCA002", self.active_rules())

    def test_unused_official_typescript_mime_constant_is_not_recognized(self) -> None:
        self.write("src/server.ts", OFFICIAL_TYPESCRIPT_UNUSED_MIME_IMPORT_APP)

        self.assertIn("MCA002", self.active_rules())

    def test_empty_directory_reports_required_protocol_signals(self) -> None:
        report = self.report()

        self.assertFalse(report.ok)
        self.assertIn("MCA001", self.active_rules())
        self.assertIn("MCA002", self.active_rules())
        self.assertIn("MCA003", self.active_rules())

    def test_sensitive_browser_permission_is_a_warning(self) -> None:
        self.write("src/server.ts", READY_APP)
        self.write(
            "src/permissions.ts",
            "const metadata = { permissions: { camera: {}, microphone: {} } };",
        )

        report = self.report()
        finding = next(item for item in report.findings if item.rule_id == "MCA006")

        self.assertEqual("warning", finding.severity)
        self.assertEqual("src/permissions.ts", finding.path)
        self.assertEqual(1, finding.line)

    def test_external_origin_without_csp_is_a_warning(self) -> None:
        without_csp = READY_APP.replace(
            '_meta: { ui: { csp: { connectDomains: ["https://api.example.com"] } } }',
            "_meta: { ui: {} }",
        )
        without_csp += (
            '\nconst response = await fetch("https://api.example.com/weather");\n'
        )
        self.write("src/server.ts", without_csp)

        self.assertIn("MCA007", self.active_rules())

    def test_wildcard_csp_domain_is_an_error(self) -> None:
        unsafe = READY_APP.replace(
            'connectDomains: ["https://api.example.com"]',
            'connectDomains: ["*"]',
        )
        self.write("src/server.ts", unsafe)

        report = self.report()
        finding = next(item for item in report.findings if item.rule_id == "MCA008")

        self.assertEqual("error", finding.severity)

    def test_secret_like_value_is_an_error(self) -> None:
        token = "sk-" + "a" * 32
        self.write("src/server.ts", READY_APP + f'\nconst API_KEY = "{token}";\n')

        report = self.report()
        finding = next(item for item in report.findings if item.rule_id == "MCA009")

        self.assertEqual("error", finding.severity)
        self.assertEqual("src/server.ts", finding.path)

    def test_missing_structured_content_and_text_fallback_are_warnings(self) -> None:
        minimal = """
const RESOURCE_URI = "ui://demo/app.html";
const mimeType = "text/html;profile=mcp-app";
const tool = { _meta: { ui: { resourceUri: RESOURCE_URI } } };
""".strip()
        self.write("server.ts", minimal)

        rules = self.active_rules()

        self.assertIn("MCA004", rules)
        self.assertIn("MCA005", rules)

    def test_ignored_directories_and_large_files_are_not_read(self) -> None:
        self.write("src/server.ts", READY_APP)
        self.write("node_modules/unsafe.js", "window.postMessage({}, '*')")
        self.write("dist/bundle.js", "window.postMessage({}, '*')")
        self.write("src/large.js", "x" * 101)

        report = scan_repository(self.root, max_file_bytes=100)

        self.assertEqual(0, report.files_scanned)
        self.assertEqual(2, report.files_skipped)

    @unittest.skipIf(
        os.name == "nt", "Creating symlinks may require Windows developer mode"
    )
    def test_directory_symlink_is_not_traversed(self) -> None:
        with tempfile.TemporaryDirectory() as outside_dir:
            outside = Path(outside_dir)
            (outside / "unsafe.ts").write_text(
                "const metadata = { permissions: { camera: {} } };", encoding="utf-8"
            )
            (self.root / "escape").symlink_to(outside, target_is_directory=True)
            self.write("src/server.ts", READY_APP)

            self.assertNotIn("MCA006", self.active_rules())

    def test_missing_path_raises_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not exist"):
            scan_repository(self.root / "missing")


if __name__ == "__main__":
    unittest.main()
