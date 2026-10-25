import csv
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "audit" / "covid_module_field_coverage_2020_v1.csv"


class CovidModuleFieldCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_covid_module_coverage_audit.py")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        with LEDGER.open(encoding="utf-8-sig", newline="") as stream:
            cls.rows = list(csv.DictReader(stream))
        cls.by_code = {row["field"].lower(): row for row in cls.rows}

    def test_every_official_dictionary_field_has_one_review_disposition(self):
        self.assertEqual(len(self.rows), 100)
        self.assertEqual(len(self.by_code), 100)
        self.assertEqual(sum(row["coverage_status"] == "mapped candidate" for row in self.rows), 77)
        self.assertEqual(sum(row["coverage_status"] == "reviewed non-E/P field" for row in self.rows), 23)
        self.assertTrue(all(row["review_rationale"].strip() for row in self.rows))

    def test_derived_quarantine_and_network_outcomes_are_mapped(self):
        self.assertEqual(self.by_code["xquarantined"]["role"], "E")
        self.assertEqual(self.by_code["vb002_s1"]["role"], "P")
        self.assertEqual(self.by_code["vb002_s2"]["role"], "P")
        self.assertEqual(self.by_code["vb002_s3"]["role"], "P")

    def test_conditional_test_dates_are_explicitly_timing_metadata(self):
        self.assertEqual(self.by_code["vb012_1"]["disposition"], "conditional timing component")
        self.assertEqual(self.by_code["vb012_2"]["disposition"], "conditional timing component")


if __name__ == "__main__":
    unittest.main()
