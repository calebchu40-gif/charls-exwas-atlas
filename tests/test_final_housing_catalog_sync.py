import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FinalHousingCatalogSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/food_environment_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.rows = list(csv.DictReader(f))
        with (ROOT / "audit/ep_concept_source_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.index = list(csv.DictReader(f))
        cls.site = json.loads((ROOT / "site-prototype/dist/food_environment_v1.json").read_text(encoding="utf-8"))

    def test_air_cleaner_alias_is_marked_as_same_exposure(self):
        row = next(r for r in self.rows if r["concept_id"] == "air_cleaner" and r["wave"] == "2015")
        self.assertIn("Catalog alias only", row["caveat"])
        self.assertIn("same 2015 I027_W3", row["caveat"])
        self.assertEqual(row["code_value_labels"], "1=Yes; 2=No")
        concept = next(c for c in self.site if c["concept_id"] == "air_cleaner")
        field = next(f for f in concept["source_fields"] if f["wave"] == "2015")
        self.assertIn("Do not count as a distinct exposure", field["note"])

    def test_2018_dwelling_area_fields_keep_distinct_routes_and_units(self):
        selected = [r for r in self.rows if r["concept_id"] == "dwelling_area" and r["wave"] == "2018"]
        self.assertEqual({r["code"] for r in selected}, {"i000_w4_11", "i000_w4_12"})
        by_code = {r["code"]: r for r in selected}
        self.assertIn("non-ownership route", by_code["i000_w4_11"]["mapping_status"])
        self.assertIn("ownership route", by_code["i000_w4_12"]["mapping_status"])
        for row in selected:
            self.assertIn("not substitutes", row["caveat"])
            self.assertIn("cross-wave equivalence is unapproved", row["caveat"])
        concept = next(c for c in self.site if c["concept_id"] == "dwelling_area")
        fields = {f["code"]: f for f in concept["source_fields"] if f["wave"] == "2018"}
        self.assertEqual(fields["i000_w4_11"]["unit"], "square metres")
        self.assertEqual(fields["i000_w4_12"]["unit"], "square metres")

    def test_source_index_matches_reviewed_mapping_status(self):
        keys = {
            (r["wave"], r["code"].lower(), r["concept_id"]): r["mapping_status"]
            for r in self.rows
            if (r["concept_id"], r["wave"], r["code"].lower()) in {
                ("air_cleaner", "2015", "i027_w3"),
                ("dwelling_area", "2018", "i000_w4_11"),
                ("dwelling_area", "2018", "i000_w4_12"),
            }
        }
        for (wave, code, concept), status in keys.items():
            row = next(r for r in self.index if r["Source.File"].endswith("food_environment_crosswalk_v1.csv") and r["Wave"] == wave and r["Source.Code"].lower() == code and concept in r["Source.Concept.ID"].split(" | "))
            self.assertEqual(row["Mapping.Status"], status)


if __name__ == "__main__":
    unittest.main()
