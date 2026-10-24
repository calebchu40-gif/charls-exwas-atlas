from __future__ import annotations

import json
import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BloodAssayMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((ROOT / "site-prototype/dist/blood_biomarkers_v1.json").read_text(encoding="utf-8"))

    def test_2011_guide_methods_are_populated_for_11_chemistry_analytes(self):
        rows = [r for r in self.rows if r["wave"] == "2011" and r["assay_method"]]
        self.assertEqual(len(rows), 11)
        self.assertTrue(all(r["within_assay_cv"] and r["between_assay_cv"] and r["guide_reported_detection_range"] for r in rows))
        self.assertEqual(next(r for r in rows if r["concept_id"] == "blood_crp")["assay_method"], "Immunoturbidimetric assay")
        self.assertEqual(next(r for r in rows if r["concept_id"] == "blood_hba1c")["within_assay_cv"], "1.90%")

    def test_2015_metadata_is_not_inherited_from_2011(self):
        rows = [r for r in self.rows if r["wave"] == "2015" and r["concept_id"] != "blood_collection_metadata"]
        self.assertEqual(len(rows), 16)
        for row in rows:
            self.assertEqual(row["assay_method"], "")
            self.assertEqual(row["within_assay_cv"], "")
            self.assertEqual(row["between_assay_cv"], "")
            self.assertEqual(row["guide_reported_detection_range"], "")
            self.assertIn("do not inherit 2011", row["assay_metadata_status"])

    def test_2011_cbc_absence_is_stated_and_unit_source_kept(self):
        cbc = [r for r in self.rows if r["wave"] == "2011" and r["domain"] == "血常规"]
        self.assertEqual(len(cbc), 5)
        self.assertTrue(all("not analyte-specific" in r["assay_metadata_status"] for r in cbc))
        self.assertTrue(all(not r["assay_method"] and not r["guide_reported_detection_range"] for r in cbc))
        self.assertEqual(next(r for r in cbc if r["concept_id"] == "blood_wbc")["source_unit_text"], "in thousands")
        self.assertEqual(next(r for r in cbc if r["concept_id"] == "blood_mcv")["source_unit_text"], "not stated in CBC summary table")

    def test_guide_ranges_are_not_labeled_as_lod(self):
        self.assertTrue(all("guide_reported_detection_range" in r for r in self.rows))
        self.assertTrue(all("Guide-reported detection range" not in r["assay_metadata_status"] for r in self.rows))

    def test_2015_release_note_inventory_matches_crosswalk(self):
        expected_2015 = {
            "bl_fasting", "bl_wbc", "bl_hgb", "bl_hct", "bl_mcv", "bl_plt",
            "bl_tg", "bl_top_coding_tg", "bl_crea", "bl_bun", "bl_hdl", "bl_ldl",
            "bl_cho", "bl_glu", "bl_ua", "bl_cysc", "bl_crp", "bl_hbalc",
        }
        with (ROOT / "audit/blood_biomarker_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            crosswalk = list(csv.DictReader(stream))
        wave3 = [row for row in crosswalk if row["wave"] == "2015"]
        self.assertEqual({row["variable"] for row in wave3}, expected_2015)
        self.assertEqual(len({row["concept_id"] for row in wave3 if row["concept_id"] != "blood_collection_metadata"}), 16)
        public_wave3 = [row for row in self.rows if row["wave"] == "2015"]
        self.assertEqual({row["variable"] for row in public_wave3}, expected_2015)
        official_note = (ROOT / "sources_official/CHARLS_2015_Blood_Release_Note_extracted.txt").read_text(encoding="utf-8")
        for variable in expected_2015:
            self.assertIn(variable, official_note)
        self.assertTrue(all(row["weight_field"] == "Blood_weight" for row in wave3))


if __name__ == "__main__":
    unittest.main()
