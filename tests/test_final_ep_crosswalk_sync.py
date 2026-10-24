import csv
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


if __name__ == "__main__":
    unittest.main()
