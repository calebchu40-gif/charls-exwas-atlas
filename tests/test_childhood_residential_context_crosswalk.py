import csv
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ChildhoodResidentialContextCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "audit/childhood_residential_context_crosswalk_v1.csv"
        with path.open(encoding="utf-8-sig", newline="") as f:
            cls.rows = list(csv.DictReader(f))

    def test_only_2013_is_mapped_and_categories_match_sources(self):
        self.assertEqual(len(self.rows), 1)
        row = self.rows[0]
        self.assertEqual((row["wave"], row["code"]), ("2013", "bb006"))
        self.assertEqual(row["value_labels"], "1=Village; 2=City/Town")
        self.assertIn("cross-wave harmonization is not established", row["mapping_status"])

    def test_reinterview_carry_forward_and_2011_conflict_are_disclosed(self):
        caveat = self.rows[0]["caveat"]
        self.assertIn("may be carried forward", caveat)
        self.assertIn("2011 Codebook reverses them", caveat)
        self.assertIn("do not combine 2011/2013 codes", caveat)

    def test_source_documents_support_2013_labels_and_route(self):
        row = self.rows[0]
        questionnaire = (ROOT / row["value_label_source"].split("; ")[0]).read_bytes().replace(b"\x00", b"").decode("utf-8", errors="replace")
        start = questionnaire.lower().find("bb006 where did you mainly live before you were 16 years old")
        self.assertGreaterEqual(start, 0)
        item = questionnaire[start:start + 1100]
        self.assertIn("1. Village", item)
        self.assertIn("2. City/Town", item)
        normalized = re.sub(r"\s+", " ", questionnaire).lower()
        self.assertIn("if xrtype = reiw and bb006 in the last wave is not missing", normalized)

    def test_public_catalog_contains_candidate_with_caveat(self):
        rows = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))
        found = [r for r in rows if r.get("Variable.Name", "").lower() == "bb006" and r.get("Source.Wave") == "2013"]
        self.assertEqual(len(found), 1)
        self.assertIn("carried forward", found[0].get("Harmonization.Status", "").lower())


if __name__ == "__main__":
    unittest.main()
