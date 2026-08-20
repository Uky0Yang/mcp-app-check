from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mcp_app_check.rules import scan_repository
from mcp_app_check.sarif import render_sarif
from tests.fixtures import READY_APP


class SarifTests(unittest.TestCase):
    def test_sarif_declares_version_2_1_0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = scan_repository(Path(directory))

        payload = json.loads(render_sarif(report))

        self.assertEqual("2.1.0", payload["version"])

    def test_sarif_identifies_mcp_app_check_driver(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = scan_repository(Path(directory))

        payload = json.loads(render_sarif(report))

        self.assertEqual("mcp-app-check", payload["runs"][0]["tool"]["driver"]["name"])

    def test_sarif_maps_error_to_source_location(self) -> None:
        unsafe = READY_APP.replace(
            'connectDomains: ["https://api.example.com"]',
            'connectDomains: ["*"]',
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src" / "server.ts"
            source.parent.mkdir()
            source.write_text(unsafe, encoding="utf-8")
            report = scan_repository(root)

        payload = json.loads(render_sarif(report))
        result = next(
            item for item in payload["runs"][0]["results"] if item["ruleId"] == "MCA008"
        )
        location = result["locations"][0]["physicalLocation"]

        self.assertEqual(
            ("error", "src/server.ts", 8),
            (
                result["level"],
                location["artifactLocation"]["uri"],
                location["region"]["startLine"],
            ),
        )


if __name__ == "__main__":
    unittest.main()
