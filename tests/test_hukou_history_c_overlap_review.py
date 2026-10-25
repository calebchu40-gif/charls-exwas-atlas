import csv
import json
import unittest
from pathlib import Path

from scripts.build_ep_atlas_metadata import FINALIZATION_PIPELINE_SCRIPTS, FULL_PIPELINE_SCRIPTS

ROOT = Path(__file__).resolve().parents[1]


class HukouHistoryOverlapReviewTests(unittest.TestCase):
    def test_sync_runs_after_crosswalk_propagation_and_before_final_shard(self):
        for pipeline in (FULL_PIPELINE_SCRIPTS, FINALIZATION_PIPELINE_SCRIPTS):
            self.assertLess(pipeline.index("propagate_ep_crosswalk_status.py"), pipeline.index("apply_hukou_history_c_overlap_review.py"))
            last_shard = max(i for i, name in enumerate(pipeline) if name == "site_catalog_shards.py")
            self.assertLess(pipeline.index("apply_hukou_history_c_overlap_review.py"), last_shard)

    def test_seven_source_linked_rows_keep_routes_and_historical_context(self):
        with (ROOT / "audit/hukou_history_c_overlap_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            reviewed = list(csv.DictReader(f))
        self.assertEqual(len(reviewed), 7)
        self.assertEqual(len({(r["wave"], r["code"].lower(), r["module"].lower()) for r in reviewed}), 7)
        self.assertTrue(all("sources_official/" in r["official_sources"] for r in reviewed))
        self.assertTrue(all("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" in r["official_sources"] for r in reviewed if r["wave"] == "2011"))
        source_review = [r for r in reviewed if r["wave"] == "2011"]
        self.assertTrue(all("Baseline_Household_Questionnaire_extracted.txt" in r["official_sources"] for r in source_review))
        self.assertTrue(all(any(token in r["caveat"].lower() for token in ("asked only", "only asked", "route only when")) for r in reviewed))
        self.assertTrue(all("reviewed" in r["mapping_status"].lower() for r in reviewed))
        catalog = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        keys = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in reviewed}
        rows = [r for r in catalog if (r["Source.Wave"], r["Variable.Name"].lower(), r["Data.File.Name"].lower()) in keys]
        self.assertEqual(len(rows), 7)
        self.assertTrue(all(r["epcf"].lower() == "c" for r in rows))
        self.assertTrue(all(r["subcategory"] == "historical hukou/location context exposure overlap" for r in rows))
        self.assertTrue(all("must not adjust for itself" in r["Review.Flag"] for r in rows))


if __name__ == "__main__":
    unittest.main()
