from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ActionMetadataTests(unittest.TestCase):
    def test_action_is_a_self_installing_composite_action(self) -> None:
        metadata = (ROOT / "action.yml").read_text(encoding="utf-8")

        self.assertIn("using: composite", metadata)
        self.assertIn("actions/setup-python@v7", metadata)
        self.assertIn("github.action_path", metadata)

    def test_ci_runs_the_local_action(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("action-smoke:", workflow)
        self.assertIn("uses: ./", workflow)

    def test_action_forwards_optional_output_path(self) -> None:
        metadata = (ROOT / "action.yml").read_text(encoding="utf-8")

        self.assertIn("INPUT_OUTPUT: ${{ inputs.output }}", metadata)

    def test_ci_uploads_sarif_with_current_codeql_action(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("github/codeql-action/upload-sarif@v4", workflow)


if __name__ == "__main__":
    unittest.main()
