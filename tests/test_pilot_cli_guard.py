"""Ensure the protected pilot never runs on a help or default invocation."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    ROOT / "scripts" / "run_2011_water_blood_pilot.py",
    ROOT / "scripts" / "run_2011_household_environment_blood_extension.py",
)


class PilotCliGuardTests(unittest.TestCase):
    def test_help_exits_without_loading_analysis_dependencies(self) -> None:
        for script in SCRIPTS:
            with self.subTest(script=script.name):
                result = subprocess.run(
                    [sys.executable, str(script), "--help"],
                    cwd=ROOT, capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("--run", result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_default_invocation_requires_explicit_run_flag(self) -> None:
        for script in SCRIPTS:
            with self.subTest(script=script.name):
                result = subprocess.run(
                    [sys.executable, str(script)],
                    cwd=ROOT, capture_output=True, text=True, check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("--run", result.stderr)
                self.assertNotIn('"run": "complete"', result.stdout)


if __name__ == "__main__":
    unittest.main()
