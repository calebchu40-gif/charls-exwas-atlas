"""Tests for the pilot-105 manifest derived from the frozen K=150 register.

The pilot batch must remain a *pure subset* of the frozen family: no new
hypotheses, no change of family, and the fasting-blocked endpoints must never
carry an estimable status.
"""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_wave1_pilot105_manifest as pilot  # noqa: E402


class Pilot105ManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = pilot.build()

    def test_shape_is_exactly_seven_by_fifteen(self):
        self.assertEqual(len(self.rows), 105)
        self.assertEqual(len({row["contrast_id"] for row in self.rows}), 7)
        self.assertEqual(len({row["phenotype_concept_id"] for row in self.rows}), 15)
        pairs = {(row["contrast_id"], row["phenotype_concept_id"]) for row in self.rows}
        self.assertEqual(len(pairs), 105)

    def test_fasting_blocked_endpoints_are_never_estimable(self):
        blocked = [row for row in self.rows
                   if row["analysis_status"] == pilot.BLOCKED_STATUS]
        self.assertEqual(len(blocked), 14)
        self.assertEqual({row["phenotype_concept_id"] for row in blocked},
                         {"blood_glucose", "blood_triglycerides"})
        for row in blocked:
            self.assertIn("qc1_va003", row["status_reason"])
        open_rows = [row for row in self.rows if row["analysis_status"] == pilot.OPEN_STATUS]
        self.assertEqual(len(open_rows), 91)
        self.assertFalse({row["phenotype_concept_id"] for row in open_rows}
                         & {"blood_glucose", "blood_triglycerides"})

    def test_every_row_stays_inside_the_frozen_parent_family(self):
        for row in self.rows:
            self.assertEqual(row["parent_family_id"], pilot.PARENT_FAMILY)
            self.assertEqual(row["parent_family_size"], "150")
            self.assertEqual(row["wave"], "2011")

    def test_hypothesis_ids_are_unique_and_borrowed_from_the_register(self):
        with pilot.REGISTER.open(newline="", encoding="utf-8-sig") as handle:
            register_ids = {row["hypothesis_id"] for row in csv.DictReader(handle)}
        ids = [row["hypothesis_id"] for row in self.rows]
        self.assertEqual(len(set(ids)), len(ids))
        self.assertTrue(set(ids).issubset(register_ids),
                        "pilot manifest must not invent hypothesis IDs")

    def test_no_pilot_row_targets_a_scale_up_only_exposure(self):
        exposures = {row["exposure_concept_id"] for row in self.rows}
        self.assertEqual(exposures, {"running_water_at_residence", "cooking_fuel_main"})

    def test_written_file_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pilot105.csv"
            pilot.write(self.rows, path)
            with path.open(newline="", encoding="utf-8") as handle:
                written = list(csv.DictReader(handle))
        self.assertEqual(len(written), 105)
        self.assertEqual(set(written[0]), set(pilot.FIELDS))

    def test_summary_counts(self):
        summary = pilot.summarise(self.rows)
        self.assertEqual(summary["rows"], 105)
        self.assertEqual(summary["by_status"][pilot.BLOCKED_STATUS], 14)
        self.assertEqual(summary["by_status"][pilot.OPEN_STATUS], 91)


if __name__ == "__main__":
    unittest.main()
