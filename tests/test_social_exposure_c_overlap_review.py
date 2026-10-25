import csv
import json
import unittest
from pathlib import Path

from scripts.build_ep_atlas_metadata import FINALIZATION_PIPELINE_SCRIPTS, FULL_PIPELINE_SCRIPTS

ROOT = Path(__file__).resolve().parents[1]


class SocialExposureOverlapReviewTests(unittest.TestCase):
    def test_sync_runs_after_crosswalk_propagation_and_before_final_shard(self):
        for pipeline in (FULL_PIPELINE_SCRIPTS, FINALIZATION_PIPELINE_SCRIPTS):
            self.assertLess(pipeline.index("propagate_ep_crosswalk_status.py"), pipeline.index("apply_social_exposure_c_overlap_review.py"))
            last_shard = max(i for i, name in enumerate(pipeline) if name == "site_catalog_shards.py")
            self.assertLess(pipeline.index("apply_social_exposure_c_overlap_review.py"), last_shard)

    def test_four_exact_social_links_preserve_storage_and_route_limits(self):
        with (ROOT / "audit/social_exposure_c_overlap_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            reviewed = list(csv.DictReader(f))
        self.assertEqual(len(reviewed), 4)
        self.assertEqual({(r["wave"], r["code"].lower()) for r in reviewed}, {
            ("2011", "da056s8"), ("2020", "xsoctype_7_"),
            ("2013", "db022_w2_9_1_s64"), ("2013", "db022_w2_9_2_s64"),
        })
        self.assertTrue(all("sources_official/" in r["official_sources"] for r in reviewed))
        social = json.loads((ROOT / "site-prototype/dist/social_exposures_v1.json").read_text(encoding="utf-8"))
        participation = next(x for x in social if x["concept_id"] == "social_participation")
        wave5 = next(x for x in participation["source_fields"] if x["wave"] == "2020" and x["code"].lower() == "xsoctype_7_")
        self.assertIn("CHARLS_2020_Questionnaire_English_extracted.txt", wave5["questionnaire_source"])
        self.assertIn("CHARLS_2020_Codebook_extracted.txt", wave5["value_label_source"])
        rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        keys = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in reviewed}
        catalog = [r for r in rows if (r["Source.Wave"], r["Variable.Name"].lower(), r["Data.File.Name"].lower()) in keys]
        self.assertEqual(len(catalog), 4)
        self.assertTrue(all(r["epcf"].lower() == "c" for r in catalog))
        self.assertTrue(all(r["subcategory"] == "social participation/care exposure overlap" for r in catalog))
        self.assertTrue(all("must not adjust for itself" in r["Review.Flag"] for r in catalog))
        self.assertTrue(all("route" in r["Review.Flag"].lower() for r in catalog))
        for row in catalog:
            if row["Variable.Name"].lower().startswith("db022_"):
                self.assertIn("No Observations", row["Review.Flag"])
                self.assertIn("unselected", row["Review.Flag"].lower())
                self.assertIn("category 15", row["Review.Flag"].lower())
                self.assertIn("suffix is a field identifier", row["Review.Flag"].lower())
            if row["Variable.Name"].lower() == "da056s8":
                self.assertIn("do not infer no from absence", row["Review.Flag"].lower())


if __name__ == "__main__":
    unittest.main()
