import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CurrentValueLabelQueueTests(unittest.TestCase):
    def test_documented_role_totals_and_pending_counts_match_current_shards(self):
        counts = {}
        for role in ("e", "p", "c"):
            rows = json.loads((ROOT / f"site-prototype/dist/catalog_{role}.json").read_text(encoding="utf-8"))
            pending = sum(row.get("Value.Label.Review", "").strip().lower() == "not yet reviewed" for row in rows)
            counts[role] = (len(rows), pending)

        document = (ROOT / "audit/current_value_label_review_queue_2026-10-23.md").read_text(encoding="utf-8")
        expected_rows = {
            "e": r"\| E exposure candidates \| ([\d,]+) \| ([\d,]+) \|",
            "p": r"\| P phenotype candidates \| ([\d,]+) \| ([\d,]+) \|",
            "c": r"\| C covariate/measurement metadata \| ([\d,]+) \| ([\d,]+) \|",
        }
        for role, pattern in expected_rows.items():
            match = re.search(pattern, document)
            self.assertIsNotNone(match, role)
            self.assertEqual(tuple(int(value.replace(",", "")) for value in match.groups()), counts[role], role)

    def test_keyword_hits_are_not_described_as_an_adjustment_set(self):
        document = (ROOT / "audit/current_value_label_review_queue_2026-10-23.md").read_text(encoding="utf-8")
        self.assertIn("keyword discovery only; not a reviewed covariate or adjustment recommendation", document)
        self.assertIn("It is a search lead, not a selected adjustment set", document)


if __name__ == "__main__":
    unittest.main()
