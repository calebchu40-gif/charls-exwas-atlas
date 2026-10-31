"""Tests for the aggregate-only fasting diagnostic.

The diagnostic must never emit respondent rows, must aggregate only, and must
refuse to run without an explicit approval flag.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_wave1_fasting_code_distribution as fasting  # noqa: E402


def records():
    return [
        {"qc1_va003": 1, "newglu": 90.0, "newtg": 100.0},
        {"qc1_va003": 1, "newglu": 110.0, "newtg": 120.0},
        {"qc1_va003": 2, "newglu": 140.0, "newtg": 180.0},
        {"qc1_va003": 2, "newglu": 160.0, "newtg": 200.0},
        {"qc1_va003": None, "newglu": 120.0, "newtg": 150.0},
        {"qc1_va003": "", "newglu": 130.0, "newtg": 160.0},
        {"qc1_va003": 1, "newglu": None, "newtg": "not-a-number"},
    ]


class SummariseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = fasting.summarise(records())

    def test_counts_and_nulls(self):
        self.assertEqual(self.summary["rows"], 7)
        self.assertEqual(self.summary["code_counts"], {"1": 3, "2": 2})
        self.assertEqual(self.summary["null_code_count"], 2)

    def test_means_are_aggregated_per_code(self):
        glucose = self.summary["outcomes"]["newglu"]
        self.assertEqual(glucose["1"]["n"], 2)
        self.assertAlmostEqual(glucose["1"]["mean"], 100.0, places=6)
        self.assertEqual(glucose["2"]["n"], 2)
        self.assertAlmostEqual(glucose["2"]["mean"], 150.0, places=6)

    def test_invalid_outcome_values_are_ignored(self):
        triglycerides = self.summary["outcomes"]["newtg"]
        self.assertEqual(triglycerides["1"]["n"], 2)
        self.assertAlmostEqual(triglycerides["1"]["mean"], 110.0, places=6)

    def test_output_contains_aggregates_only(self):
        text = repr(self.summary)
        for forbidden in ("ID", "respondent", "qc1_vb002"):
            self.assertNotIn(forbidden, text)
        self.assertTrue(all(isinstance(value, (int, float, str, dict))
                            for value in self.summary["code_counts"].values()))
        # every outcome entry is {code: {n, mean}} — never a value list
        for field in self.summary["outcomes"].values():
            for entry in field.values():
                self.assertEqual(set(entry), {"n", "mean"})

    def test_empty_input_is_still_well_formed(self):
        summary = fasting.summarise([])
        self.assertEqual(summary["rows"], 0)
        self.assertEqual(summary["code_counts"], {})
        self.assertEqual(summary["null_code_count"], 0)
        self.assertEqual(summary["outcomes"]["newglu"], {})


class GuardrailTests(unittest.TestCase):
    def test_flag_constant_is_the_documented_gate(self):
        self.assertEqual(fasting.REQUIRED_FLAG, "--run")

    def test_running_without_the_flag_is_refused(self):
        with self.assertRaises(SystemExit) as raised:
            fasting.main(["--dta", "missing.dta", "--out", "missing.json"])
        self.assertNotEqual(raised.exception.code, 0)

    def test_module_defines_no_writing_side_effects(self):
        # Importing and summarising must not create files.
        before = set(Path.cwd().iterdir())
        fasting.summarise(records())
        self.assertEqual(before, set(Path.cwd().iterdir()))


if __name__ == "__main__":
    unittest.main()
