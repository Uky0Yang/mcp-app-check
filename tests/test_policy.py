import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from mcp_app_check.cli import main


class PolicyTests(unittest.TestCase):
    def test_explicit_policy_suppresses_rules_with_visible_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "policy.json"
            config.write_text(
                json.dumps(
                    {"ignore": ["MCA001", "MCA002", "MCA003"], "fail_on": "none"}
                ),
                encoding="utf-8",
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main([directory, "--config", str(config), "--format", "json"])
            data = json.loads(output.getvalue())
            self.assertEqual(code, 0)
            self.assertGreaterEqual(data["findings_suppressed"], 3)
            self.assertFalse(any(f["rule_id"] == "MCA001" for f in data["findings"]))

    def test_invalid_policy_is_error_not_silent_disable(self):
        for value in (
            {"ignore": ["MCA999"]},
            {"ignore": "MCA001"},
            {"fail_on": "typo"},
            {"unexpected": True},
            [],
        ):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                config = Path(directory) / "policy.json"
                config.write_text(json.dumps(value), encoding="utf-8")
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(main([directory, "--config", str(config)]), 2)

    def test_cli_ignore_is_validated(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(main([directory, "--ignore", "MCA999"]), 2)

    def test_no_automatic_policy_and_cli_threshold_precedence(self):
        with tempfile.TemporaryDirectory() as directory:
            policy = Path(directory) / "mcp-app-check.json"
            policy.write_text('{"fail_on": "none"}', encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([directory]), 1)
                self.assertEqual(main([directory, "--config", str(policy)]), 0)
                self.assertEqual(
                    main([directory, "--config", str(policy), "--fail-on", "error"]), 1
                )
