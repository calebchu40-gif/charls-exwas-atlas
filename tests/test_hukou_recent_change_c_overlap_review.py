import csv
import json
import unittest
from pathlib import Path

from scripts.build_ep_atlas_metadata import FINALIZATION_PIPELINE_SCRIPTS, FULL_PIPELINE_SCRIPTS

ROOT = Path(__file__).resolve().parents[1]


class HukouRecentChangeOverlapTests(unittest.TestCase):
    def test_source_linking_runs_after_crosswalks_before_sharding(self):
        for pipeline in (FULL_PIPELINE_SCRIPTS, FINALIZATION_PIPELINE_SCRIPTS):
            self.assertLess(pipeline.index("propagate_ep_crosswalk_status.py"), pipeline.index("apply_hukou_recent_change_c_overlap_review.py"))
            self.assertLess(pipeline.index("apply_hukou_lifecourse_c_overlap_review.py"), pipeline.index("apply_hukou_recent_change_c_overlap_review.py"))
            last_shard = max(i for i, name in enumerate(pipeline) if name == "site_catalog_shards.py")
            self.assertLess(pipeline.index("apply_hukou_recent_change_c_overlap_review.py"), last_shard)

    def test_eleven_exact_recent_change_links_retain_wave_and_conditional_semantics(self):
        with (ROOT / "audit/hukou_recent_change_c_overlap_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            audit = list(csv.DictReader(f))
        expected = {
            ("2013", "bc001_w2_1"), ("2013", "bc001_w2_2"), ("2013", "bc001_w2_3"),
            ("2013", "bc005_w2_1"), ("2013", "bc005_w2_2"),
            *((wave, code) for wave in ("2015", "2018") for code in ("bc002_w3", "bc002_w3_2", "bc002_w3_5")),
        }
        self.assertEqual({(r["wave"], r["code"].lower()) for r in audit}, expected)
        self.assertTrue(all("sources_official/" in r["official_sources"] for r in audit))
        rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        keys = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in audit}
        found = [r for r in rows if (r["Source.Wave"], r["Variable.Name"].lower(), r["Data.File.Name"].lower()) in keys]
        self.assertEqual(len(found), 11)
        self.assertTrue(all(r["epcf"].lower() == "c" for r in found))
        self.assertTrue(all(r["subcategory"] == "recent hukou change exposure overlap; conditional context candidate" for r in found))
        self.assertTrue(all("must not adjust for itself" in r["Review.Flag"] for r in found))
        labels = {r["code"].lower(): r["value_labels"] for r in audit}
        self.assertIn("5=No change", labels["bc001_w2_2"])
        self.assertIn("6=No change", labels["bc001_w2_3"])
        caveats = {(r["wave"], r["code"].lower()): r["caveat"] for r in audit}
        self.assertIn("ZBC001 nonresponse", caveats[("2015", "bc002_w3")])
        self.assertIn("sixth category", caveats[("2015", "bc002_w3_5")])
        self.assertIn("reinterview route", caveats[("2018", "bc002_w3")])
        self.assertIn("BC005_W2_1=1", caveats[("2013", "bc005_w2_2")])


class KeywordEPCOverlapReviewTests(unittest.TestCase):
    def test_exact_source_reviewed_overlap_sync_runs_before_sharding(self):
        for pipeline in (FULL_PIPELINE_SCRIPTS, FINALIZATION_PIPELINE_SCRIPTS):
            self.assertLess(pipeline.index("apply_hukou_recent_change_c_overlap_review.py"), pipeline.index("apply_keyword_epc_overlap_review.py"))
            last_shard = max(i for i, name in enumerate(pipeline) if name == "site_catalog_shards.py")
            self.assertLess(pipeline.index("apply_keyword_epc_overlap_review.py"), last_shard)

    def test_only_forty_exact_questionnaire_codebook_ep_overlaps_are_linked(self):
        with (ROOT / "audit/keyword_epc_overlap_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            audit = list(csv.DictReader(f))
        self.assertEqual(len(audit), 40)
        self.assertTrue({("2011", code) for code in ("da030_2", "da049", "da062_1", "da065_1", "da070_2", "da071_2")} <=
                        {(r["wave"], r["code"].lower()) for r in audit})
        self.assertTrue(all(r["official_questionnaire"].startswith("sources_official/") for r in audit))
        self.assertTrue(all(r["official_codebook"].startswith("sources_official/") for r in audit))
        rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        keys = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in audit}
        found = [r for r in rows if (r["Source.Wave"], r["Variable.Name"].lower(), r["Data.File.Name"].lower()) in keys]
        self.assertEqual(len(found), 40)
        self.assertTrue(all("its own focal association" in r["Review.Flag"] for r in found))
        self.assertTrue(all("not a default adjustment set" in r["Review.Flag"] for r in found))
        self.assertFalse(any(r["Candidate.Status"].startswith("automated keyword discovery only") for r in found))

    def test_unverified_and_route_sensitive_keyword_hits_are_not_auto_linked(self):
        with (ROOT / "audit/keyword_epc_overlap_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            audit = list(csv.DictReader(f))
        keys = {(r["wave"], r["code"].lower()) for r in audit}
        self.assertNotIn(("2011", "da057_8_"), keys)
        self.assertNotIn(("2011", "da005_2_"), keys)
        self.assertNotIn(("2011", "da006_2_"), keys)
        self.assertNotIn(("2018", "da006_w4_1_2_"), keys)


if __name__ == "__main__":
    unittest.main()
