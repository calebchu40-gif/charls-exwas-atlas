import json
import unittest
from pathlib import Path

from scripts.build_ep_atlas_metadata import FINALIZATION_PIPELINE_SCRIPTS, FULL_PIPELINE_SCRIPTS
from scripts.apply_residential_history_search_label_review import GENERIC, TARGETS

ROOT = Path(__file__).resolve().parents[1]


class ResidentialHistorySearchLabelReviewTests(unittest.TestCase):
    def test_label_sync_runs_after_source_review_and_before_final_sharding(self):
        for pipeline in (FULL_PIPELINE_SCRIPTS, FINALIZATION_PIPELINE_SCRIPTS):
            self.assertIn("apply_residential_history_search_label_review.py", pipeline)
            self.assertLess(pipeline.index("apply_keyword_epc_overlap_review.py"),
                            pipeline.index("apply_residential_history_search_label_review.py"))
            last_shard = max(i for i, name in enumerate(pipeline) if name == "site_catalog_shards.py")
            self.assertLess(pipeline.index("apply_residential_history_search_label_review.py"), last_shard)

    def test_only_exact_source_reviewed_rows_receive_specific_search_labels(self):
        rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        targets = {(wave, code.casefold()): (category, subcategory)
                   for (wave, code), (category, subcategory) in TARGETS.items()}
        selected = [r for r in rows if r.get("epcf", "").casefold() == "c" and
                    r.get("subcategory") in {v[1] for v in TARGETS.values()}]
        actual = {(r["Source.Wave"], r["Variable.Name"].casefold()):
                  (r["category"], r["subcategory"]) for r in selected}
        self.assertEqual(actual, targets)
        self.assertTrue(all("Questionnaire" in r["Value.Label.Source"] and
                            "Codebook" in r["Value.Label.Source"] for r in selected))
        self.assertFalse(any(r.get("subcategory") == GENERIC for r in selected))

    def test_2011_residential_history_identity_holds_remain_untouched(self):
        rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        held = {(r["Source.Wave"], r["Variable.Name"].casefold()): r
                for r in rows if r.get("Source.Wave") == "2011" and
                r.get("Variable.Name", "").casefold() in {"bb003", "bb005"}}
        self.assertEqual(set(held), {("2011", "bb003"), ("2011", "bb005")})
        self.assertTrue(all("identity hold" in r["category"] for r in held.values()))


if __name__ == "__main__":
    unittest.main()
