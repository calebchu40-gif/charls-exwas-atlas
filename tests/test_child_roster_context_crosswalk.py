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
        for wave in ("2013", "2015"):
            for key in ("id", "childid", "hhmemberid"):
                self.assertIn((wave, key, "child"), raw_keys)
        self.assertEqual(len(mappings), 19)
        self.assertEqual(len({r["concept_id"] for r in mappings}), 12)
        for row in mappings:
            self.assertIn((row["wave"], row["code"].lower(), "child"), raw_keys)
            self.assertIn("ID, childID, and HHmemberID", row["caveat"])
            self.assertIn("validate the actual release layout", row["caveat"].lower())
            self.assertIn("clustered within respondents", row["caveat"])
            self.assertIn("validate ID/childID join", row["mapping_status"])
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
        self.assertNotIn(("2015", "cb063_w3_1"), mappings)
        phenotypes = {(r["wave"], r["code"]): r for r in rows(ROOT / "audit/child_phenotype_crosswalk_v1.csv")}
        self.assertEqual(len(phenotypes), 2)
        self.assertIn("younger than 16", phenotypes[("2015", "cb063_w3_1")]["caveat"])
        self.assertIn("older than 60", phenotypes[("2015", "cb063_w3_6")]["caveat"])

    def test_both_build_pipelines_run_child_mapping_before_catalog(self):
        for pipeline in (FULL_PIPELINE_SCRIPTS, FINALIZATION_PIPELINE_SCRIPTS):
            self.assertIn("build_child_roster_context_crosswalk.py", pipeline)
            self.assertIn("build_child_phenotype_crosswalk.py", pipeline)
            self.assertLess(
                pipeline.index("build_child_phenotype_crosswalk.py"),
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
            self.assertIn("childID", fields[key]["Harmonization.Status"])
            self.assertIn("concept-source crosswalk candidate", fields[key]["Candidate.Status"])

    def test_child_health_outcomes_are_p_only_in_the_child_analysis_unit(self):
        catalog = json.loads((ROOT / "site-prototype/dist/catalog_p.json").read_text(encoding="utf-8"))
        fields = {(row["Source.Wave"], row["Variable.Name"].lower()): row for row in catalog}
        e_catalog = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))
        e_keys = {(row["Source.Wave"], row["Variable.Name"].lower()) for row in e_catalog}
        for code in ("cb063_w3_1", "cb063_w3_6"):
            key = ("2015", code)
            self.assertIn(key, fields)
            self.assertNotIn(key, e_keys)
            self.assertIn("child-level", fields[key]["Harmonization.Status"])
            self.assertIn("childID", fields[key]["Harmonization.Status"])


if __name__ == "__main__":
    unittest.main()
