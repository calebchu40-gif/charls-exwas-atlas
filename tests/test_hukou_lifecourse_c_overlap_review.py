import csv
import json
import unittest
from pathlib import Path

from scripts.build_ep_atlas_metadata import FINALIZATION_PIPELINE_SCRIPTS, FULL_PIPELINE_SCRIPTS

ROOT = Path(__file__).resolve().parents[1]


class HukouLifecourseOverlapTests(unittest.TestCase):
    def test_source_linking_occurs_after_crosswalk_propagation_and_before_sharding(self):
        for pipeline in (FULL_PIPELINE_SCRIPTS, FINALIZATION_PIPELINE_SCRIPTS):
            self.assertLess(pipeline.index("propagate_ep_crosswalk_status.py"), pipeline.index("apply_hukou_lifecourse_c_overlap_review.py"))
            self.assertLess(pipeline.index("apply_hukou_history_c_overlap_review.py"), pipeline.index("apply_hukou_lifecourse_c_overlap_review.py"))
            last_shard = max(i for i, name in enumerate(pipeline) if name == "site_catalog_shards.py")
            self.assertLess(pipeline.index("apply_hukou_lifecourse_c_overlap_review.py"), last_shard)

    def test_sixteen_exact_historical_links_keep_routes_and_no_self_adjustment(self):
        with (ROOT / "audit/hukou_lifecourse_c_overlap_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            audit = list(csv.DictReader(f))
        expected = {(wave, code) for wave in ("2011", "2013") for code in ("bc007", "bc008", "bc009", "bc010", "bc012", "bc015", "bc017", "bc002")}
        self.assertEqual({(r["wave"], r["code"].lower()) for r in audit}, expected)
        self.assertTrue(all("sources_official/" in r["official_sources"] for r in audit))
        self.assertTrue(all(any(token in (r["value_semantics"] + r["caveat"]).lower() for token in ("conditional", "asked", "skip", "route")) for r in audit))
        rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        targets = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in audit}
        found = [r for r in rows if (r["Source.Wave"], r["Variable.Name"].lower(), r["Data.File.Name"].lower()) in targets]
        self.assertEqual(len(found), 16)
        self.assertTrue(all(r["epcf"].lower() == "c" for r in found))
        self.assertTrue(all(r["subcategory"] == "hukou life-course exposure overlap; estimand-specific context candidate" for r in found))
        self.assertTrue(all("must never adjust for itself" in r["Review.Flag"] for r in found))
        self.assertTrue(all("conditional" in r["Review.Flag"].lower() or "only asked" in r["Review.Flag"].lower() for r in found))


if __name__ == "__main__":
    unittest.main()
