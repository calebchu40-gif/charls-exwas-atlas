import csv
import json
import unittest
from pathlib import Path

from scripts.build_ep_atlas_metadata import FINALIZATION_PIPELINE_SCRIPTS, FULL_PIPELINE_SCRIPTS

ROOT = Path(__file__).resolve().parents[1]


class PartnerContextOverlapReviewTests(unittest.TestCase):
    def test_sync_runs_after_crosswalk_propagation_and_before_final_shard(self):
        for pipeline in (FULL_PIPELINE_SCRIPTS, FINALIZATION_PIPELINE_SCRIPTS):
            self.assertLess(pipeline.index("propagate_ep_crosswalk_status.py"), pipeline.index("apply_partner_context_c_overlap_review.py"))
            last_shard = max(i for i, name in enumerate(pipeline) if name == "site_catalog_shards.py")
            self.assertLess(pipeline.index("apply_partner_context_c_overlap_review.py"), last_shard)

    def test_exact_six_source_reviewed_links_keep_route_caveats(self):
        with (ROOT / "audit/partner_context_c_overlap_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            reviewed = list(csv.DictReader(f))
        self.assertEqual(len(reviewed), 6)
        keys = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in reviewed}
        self.assertEqual(len(keys), 6)
        self.assertTrue(all("sources_official/" in r["official_sources"] for r in reviewed))
        self.assertTrue(all("official questionnaire and codebook reviewed" in r["mapping_status"].lower() for r in reviewed))
        self.assertTrue(all(r["caveat"] and r["value_semantics"] for r in reviewed))
        catalog = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        rows = [r for r in catalog if (r["Source.Wave"], r["Variable.Name"].lower(), r["Data.File.Name"].lower()) in keys]
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(r["epcf"].lower() == "c" for r in rows))
        self.assertTrue(all(r["subcategory"] == "partner/social context exposure overlap" for r in rows))
        self.assertTrue(all("must not adjust for itself" in r["Review.Flag"] for r in rows))
        self.assertTrue(all("not an adjustment recommendation" in r["Candidate.Status"] for r in rows))


if __name__ == "__main__":
    unittest.main()
