import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


class FinalEpCrosswalkSyncTests(unittest.TestCase):
    def test_reviewed_food_mapping_statuses_match_their_final_source_crosswalk(self):
        source = {
            (r["wave"], r["code"].lower()): r
            for r in read_csv(ROOT / "audit/food_environment_crosswalk_v1.csv")
        }
        mappings = read_csv(ROOT / "audit/ep_concept_source_crosswalk_v1.csv")
        targets = [
            r for r in mappings
            if r["Source.File"] == "audit/food_environment_crosswalk_v1.csv"
            and (r["Wave"], r["Source.Code"].lower()) in source
        ]
        self.assertGreater(len(targets), 0)
        for mapping in targets:
            key = (mapping["Wave"], mapping["Source.Code"].lower())
            self.assertEqual(mapping["Mapping.Status"], source[key]["mapping_status"], key)

    def test_final_index_rebuild_follows_domain_reviews_and_precedes_summaries(self):
        text = (ROOT / "scripts/build_ep_atlas_metadata.py").read_text(encoding="utf-8")
        final_start = text.index("FINALIZATION_PIPELINE_SCRIPTS = (")
        final = text[final_start:]
        last_builder = final.rindex('"build_ep_concept_source_crosswalk.py"')
        last_weekly_review = final.rindex('"apply_weekly_household_food_expenditure_review.py"')
        first_summary_after = final.index('"summarize_ep_pair_wave_coverage.py"', last_builder)
        self.assertGreater(last_builder, last_weekly_review)
        self.assertLess(last_builder, first_summary_after)
        for script in (
            '"apply_2018_household_property_value_review.py"',
            '"apply_2018_housing_roster_context_review.py"',
            '"apply_housing_numeric_measure_review.py"',
        ):
            self.assertGreater(final.index(script, last_builder), last_builder)
            self.assertLess(final.index(script, last_builder), first_summary_after)

    def test_reviewed_housing_measure_statuses_reach_the_public_source_crosswalk(self):
        source = {
            (r["wave"], r["code"].lower()): r
            for r in read_csv(ROOT / "audit/food_environment_crosswalk_v1.csv")
        }
        reviewed_counts = {
            (wave, code)
            for wave, fields in {
                "2011": ("i012_1", "i012_2", "i012_3"),
                "2013": ("i012_1", "i012_2", "i012_3"),
                "2015": ("i012_1", "i012_2", "i012_3"),
                "2018": ("i012_1", "i012_2", "i012_3"),
                "2020": ("i011_1", "i011_2", "i011_3"),
            }.items()
            for code in fields
        }
        reviewed_area_year = {
            ("2011", "i001"), ("2013", "i001"), ("2020", "i028"),
            ("2011", "i005"), ("2013", "i005"), ("2015", "i005"),
            ("2018", "i005"), ("2020", "i002"),
        }
        for key in reviewed_counts | reviewed_area_year:
            row = source[key]
            self.assertNotIn("pending", row["mapping_status"].lower(), key)
            self.assertIn("official", row["mapping_status"].lower(), key)
            self.assertTrue(row["caveat"], key)
        self.assertIn("special values", source[("2011", "i012_1")]["mapping_status"])
        self.assertIn("cross-wave", source[("2011", "i012_1")]["caveat"])

    def test_reviewed_housing_measure_statuses_reach_browser_domain_json(self):
        import json

        data = json.loads((ROOT / "site-prototype/dist/food_environment_v1.json").read_text(encoding="utf-8"))
        fields = {
            (field["wave"], field["code"]): field
            for concept in data
            for field in concept["source_fields"]
        }
        for key in {
            ("2011", "i012_1"), ("2013", "i012_1"), ("2020", "i011_1"),
            ("2011", "i001"), ("2013", "i001"), ("2020", "i028"),
            ("2011", "i005"), ("2013", "i005"), ("2020", "i002"),
        }:
            self.assertIn("official", fields[key]["note"].lower(), key)
            self.assertNotIn("pending", fields[key]["note"].lower(), key)
        self.assertIn("special values", fields[("2020", "i011_1")]["note"])

    def test_reviewed_floor_and_entrance_measures_reach_site_and_source_index(self):
        keys = {
            ("2011", "i008"), ("2013", "i008"), ("2015", "i008"), ("2018", "i008"),
            ("2020", "i006"), ("2020", "i006_1"), ("2020", "i006_2"), ("2020", "i010"),
        }
        data = json.loads((ROOT / "site-prototype/dist/food_environment_v1.json").read_text(encoding="utf-8"))
        browser_fields = {
            (field["wave"], field["code"]): field
            for concept in data
            for field in concept["source_fields"]
        }
        source_rows = {
            (r["Wave"], r["Source.Code"].lower()): r
            for r in read_csv(ROOT / "audit/ep_concept_source_crosswalk_v1.csv")
            if r["Source.File"] == "audit/food_environment_crosswalk_v1.csv"
        }
        for key in keys:
            self.assertIn("official", browser_fields[key]["mapping_status"].lower(), key)
            self.assertNotIn("pending", browser_fields[key]["mapping_status"].lower(), key)
            self.assertEqual(source_rows[key]["Mapping.Status"], browser_fields[key]["mapping_status"], key)


if __name__ == "__main__":
    unittest.main()
