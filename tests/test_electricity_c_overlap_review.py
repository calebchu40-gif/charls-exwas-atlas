import csv
import json
import unittest
from pathlib import Path

from scripts.build_ep_atlas_metadata import FINALIZATION_PIPELINE_SCRIPTS, FULL_PIPELINE_SCRIPTS

ROOT = Path(__file__).resolve().parents[1]


class ElectricityOverlapReviewTests(unittest.TestCase):
    def test_sync_runs_after_crosswalk_propagation_and_before_final_shard(self):
        for pipeline in (FULL_PIPELINE_SCRIPTS, FINALIZATION_PIPELINE_SCRIPTS):
            self.assertLess(pipeline.index("propagate_ep_crosswalk_status.py"), pipeline.index("apply_electricity_c_overlap_review.py"))
            last_shard = max(i for i, name in enumerate(pipeline) if name == "site_catalog_shards.py")
            self.assertLess(pipeline.index("apply_electricity_c_overlap_review.py"), last_shard)

    def test_three_exact_household_access_links_preserve_person_assignment_limits(self):
        with (ROOT / "audit/electricity_c_overlap_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            reviewed = list(csv.DictReader(f))
        self.assertEqual(len(reviewed), 3)
        self.assertEqual({r["wave"] for r in reviewed}, {"2011", "2013", "2018"})
        self.assertTrue(all("sources_official/" in r["official_sources"] for r in reviewed))
        self.assertTrue(all("linkage from household referent" in r["caveat"] for r in reviewed))
        rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        keys = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in reviewed}
        catalog = [r for r in rows if (r["Source.Wave"], r["Variable.Name"].lower(), r["Data.File.Name"].lower()) in keys]
        self.assertEqual(len(catalog), 3)
        self.assertTrue(all(r["epcf"].lower() == "c" for r in catalog))
        self.assertTrue(all(r["subcategory"] == "household electricity access exposure overlap" for r in catalog))
        self.assertTrue(all("Do not interpret as personal dose" in r["Review.Flag"] for r in catalog))
        self.assertTrue(all("must not adjust for itself" in r["Review.Flag"] for r in catalog))


if __name__ == "__main__":
    unittest.main()
