import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class UnresolvedFieldIdentityTests(unittest.TestCase):
    def test_flda081_is_reviewed_context_metadata_with_da081_linkage_caveat(self):
        with (ROOT / "site-prototype/dist/catalog_c.json").open(encoding="utf-8") as stream:
            c_rows = json.load(stream)
        rows = [r for r in c_rows if r.get("Source.Wave") == "2011" and r.get("Variable.Name", "").lower() == "flda081_1"]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertIn("codebook age-category labels transcribed without frequencies", row.get("Value.Label.Review", "").lower())
        self.assertEqual(row.get("Value.Labels"), "75; 80; 85; 90; 95; 100; 105; 110; 115")
        self.assertEqual(row.get("category"), "measurement metadata")
        self.assertIn("linkage remains unverified", row.get("Harmonization.Status", ""))
        self.assertEqual(row.get("candidate_concept_ids", ""), "")
        note = (ROOT / "audit/pending_c_field_identity_review_2026-10-24.md").read_text(encoding="utf-8")
        self.assertIn("DA081", note)
        self.assertIn("一对一关系", note)
        self.assertIn("不能作为独立表型或协变量", note)
        self.assertIn("75、80、85、90、95、100、105、110、115", note)

    def test_target_age_metadata_is_absent_from_exposure_and_phenotype_shards(self):
        for role in ("e", "p"):
            with (ROOT / f"site-prototype/dist/catalog_{role}.json").open(encoding="utf-8") as stream:
                rows = json.load(stream)
            self.assertFalse(any(r.get("Source.Wave") == "2011" and r.get("Variable.Name", "").lower() == "flda081_1" for r in rows))


if __name__ == "__main__":
    unittest.main()
