import csv
import json
import unittest
from pathlib import Path

from scripts.build_ep_atlas_metadata import FINALIZATION_PIPELINE_SCRIPTS, FULL_PIPELINE_SCRIPTS

ROOT = Path(__file__).resolve().parents[1]


class ResidentialSettlementOverlapReviewTests(unittest.TestCase):
    def test_sync_runs_after_crosswalk_propagation_and_before_final_shard(self):
        for pipeline in (FULL_PIPELINE_SCRIPTS, FINALIZATION_PIPELINE_SCRIPTS):
            self.assertLess(pipeline.index("propagate_ep_crosswalk_status.py"), pipeline.index("apply_residential_settlement_c_overlap_review.py"))
            last_shard = max(i for i, name in enumerate(pipeline) if name == "site_catalog_shards.py")
            self.assertLess(pipeline.index("apply_residential_settlement_c_overlap_review.py"), last_shard)

    def test_exact_two_rows_keep_wave_specific_non_harmonization_caveats(self):
        with (ROOT / "audit/residential_settlement_c_overlap_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            reviewed = list(csv.DictReader(f))
        self.assertEqual(len(reviewed), 2)
        self.assertEqual({r["wave"] for r in reviewed}, {"2015", "2020"})
        self.assertTrue(all("sources_official/" in r["official_sources"] for r in reviewed))
        self.assertTrue(all("not hukou" in r["caveat"].lower() for r in reviewed))
        self.assertTrue(all("do not harmonize by numeric code" in r["caveat"].lower() for r in reviewed))
        rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        keys = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in reviewed}
        catalog = [r for r in rows if (r["Source.Wave"], r["Variable.Name"].lower(), r["Data.File.Name"].lower()) in keys]
        self.assertEqual(len(catalog), 2)
        self.assertTrue(all(r["epcf"].lower() == "c" for r in catalog))
        self.assertTrue(all(r["subcategory"] == "residential settlement context exposure overlap" for r in catalog))
        self.assertTrue(all("must not adjust for itself" in r["Review.Flag"] for r in catalog))


if __name__ == "__main__":
    unittest.main()
