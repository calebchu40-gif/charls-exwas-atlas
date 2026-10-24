import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class UnresolvedFieldIdentityTests(unittest.TestCase):
    def test_flda081_remains_pending_c_until_official_questionnaire_identity_is_found(self):
        with (ROOT / "site-prototype/dist/catalog_c.json").open(encoding="utf-8") as stream:
            c_rows = json.load(stream)
        rows = [r for r in c_rows if r.get("Source.Wave") == "2011" and r.get("Variable.Name", "").lower() == "flda081_1"]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.get("Value.Label.Review"), "not yet reviewed")
        self.assertEqual(row.get("candidate_concept_ids", ""), "")
        note = (ROOT / "audit/pending_c_field_identity_review_2026-10-24.md").read_text(encoding="utf-8")
        self.assertIn("exact questionnaire identity", note)
        self.assertIn("DA081", note)
        self.assertIn("Do not treat the nearby questionnaire item as proof", note)
        self.assertIn("Do not rename it as life expectancy", note)

    def test_unresolved_field_is_absent_from_exposure_and_phenotype_shards(self):
        for role in ("e", "p"):
            with (ROOT / f"site-prototype/dist/catalog_{role}.json").open(encoding="utf-8") as stream:
                rows = json.load(stream)
            self.assertFalse(any(r.get("Source.Wave") == "2011" and r.get("Variable.Name", "").lower() == "flda081_1" for r in rows))


if __name__ == "__main__":
    unittest.main()
