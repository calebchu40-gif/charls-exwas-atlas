import csv
import json
import unittest
from pathlib import Path

from scripts.build_ep_atlas_metadata import FINALIZATION_PIPELINE_SCRIPTS, FULL_PIPELINE_SCRIPTS

ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class ChildRosterContextCrosswalkTests(unittest.TestCase):
    def test_crosswalk_fields_are_official_child_module_entries(self):
        mappings = rows(ROOT / "audit/child_roster_context_crosswalk_v1.csv")
        raw = rows(ROOT / "audit/raw_variable_catalog_v1.csv")
        raw_keys = {(r["wave"], r["variable"].lower(), r["module"].lower()) for r in raw}
        self.assertEqual(len(mappings), 21)
        self.assertEqual(len({r["concept_id"] for r in mappings}), 14)
        for row in mappings:
            self.assertIn((row["wave"], row["code"].lower(), "child"), raw_keys)
            self.assertIn("numbered child-slot variables", row["caveat"])
            self.assertIn("do not assume a standalone childID", row["caveat"])
            self.assertIn("no respondent-level aggregation approved", row["mapping_status"])
            self.assertNotIn("frequency", row["value_labels"].lower())

    def test_child_record_routes_and_nonharmonized_wave_items_remain_explicit(self):
        mappings = {(r["wave"], r["code"]): r for r in rows(ROOT / "audit/child_roster_context_crosswalk_v1.csv")}
        self.assertIn("CB053=5", mappings[("2013", "cb053_2")]["caveat"])
        self.assertIn("seven-category", mappings[("2015", "cb054")]["caveat"])
        self.assertNotEqual(
            mappings[("2013", "cb070")]["concept_id"],
            mappings[("2015", "sta")]["concept_id"],
        )
        self.assertNotEqual(
            mappings[("2013", "cb071")]["concept_id"],
            mappings[("2015", "cb071_w3")]["concept_id"],
        )
        self.assertIn("under age 16", mappings[("2015", "cb063_w3_1")]["caveat"])

    def test_both_build_pipelines_run_child_mapping_before_catalog(self):
        for pipeline in (FULL_PIPELINE_SCRIPTS, FINALIZATION_PIPELINE_SCRIPTS):
            self.assertIn("build_child_roster_context_crosswalk.py", pipeline)
            self.assertLess(
                pipeline.index("build_child_roster_context_crosswalk.py"),
                pipeline.index("build_charls_atlas_catalog.py"),
            )

    def test_child_records_are_searchable_with_their_linkage_warning(self):
        catalog = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))
        fields = {
            (row["Source.Wave"], row["Variable.Name"].lower()): row
            for row in catalog
            if row.get("Data.File.Name", "").lower() == "child"
            and row.get("category") == "family and intergenerational context"
        }
        expected = {(r["wave"], r["code"].lower()) for r in rows(ROOT / "audit/child_roster_context_crosswalk_v1.csv")}
        self.assertTrue(expected.issubset(fields.keys()))
        for key in expected:
            self.assertIn("child roster slot", fields[key]["Harmonization.Status"])
            self.assertIn("concept-source crosswalk candidate", fields[key]["Candidate.Status"])


if __name__ == "__main__":
    unittest.main()
