import csv
import json
import unittest
from pathlib import Path

from scripts.build_ep_atlas_metadata import FINALIZATION_PIPELINE_SCRIPTS, FULL_PIPELINE_SCRIPTS


ROOT = Path(__file__).resolve().parents[1]


class FormalSchoolingOverlapReviewTests(unittest.TestCase):
    def test_overlap_sync_runs_after_crosswalk_propagation_before_site_sharding(self):
        for pipeline in (FULL_PIPELINE_SCRIPTS, FINALIZATION_PIPELINE_SCRIPTS):
            self.assertLess(pipeline.index("propagate_ep_crosswalk_status.py"), pipeline.index("apply_formal_schooling_c_overlap_review.py"))
            last_shard = max(i for i, name in enumerate(pipeline) if name == "site_catalog_shards.py")
            self.assertLess(pipeline.index("apply_formal_schooling_c_overlap_review.py"), last_shard)

    def test_exact_wave_c_rows_keep_exposure_link_and_route_caveat(self):
        with (ROOT / "audit/formal_schooling_c_overlap_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            reviewed = list(csv.DictReader(f))
        self.assertEqual(len(reviewed), 9)
        self.assertEqual(len({(r["wave"], r["code"].lower(), r["module"].lower()) for r in reviewed}), 9)
        self.assertTrue(all("sources_official/" in r["official_sources"] for r in reviewed))
        catalog = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        keys = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in reviewed}
        rows = [r for r in catalog if (r["Source.Wave"], r["Variable.Name"].lower(), r["Data.File.Name"].lower()) in keys]
        self.assertEqual(len(rows), 9)
        self.assertTrue(all(r["epcf"].lower() == "c" for r in rows))
        self.assertTrue(all("formal-schooling history exposure overlap" in r["subcategory"] for r in rows))
        self.assertTrue(all("not an adjustment recommendation" in r["Candidate.Status"] for r in rows))
        self.assertTrue(all("preserve its question route" in r["Candidate.Status"] for r in rows))


if __name__ == "__main__":
    unittest.main()
