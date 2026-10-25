import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CatalogCrosswalkStatusPropagationTests(unittest.TestCase):
    def test_crosswalk_mapped_ep_rows_are_not_left_as_automated_hits(self):
        rows = [
            row
            for role in ("e", "p")
            for row in json.loads((ROOT / f"site-prototype/dist/catalog_{role}.json").read_text(encoding="utf-8"))
            if row.get("Concept.Mapping.Source")
        ]
        self.assertGreaterEqual(len(rows), 6_800)
        stale = [row for row in rows
                 if row.get("Candidate.Status", "").lower().startswith(("automated discovery", "automated keyword discovery"))]
        self.assertEqual(stale, [])
        self.assertTrue(all("approved test variable" in row.get("Review.Flag", "")
                            or "not analytic inclusion" in row.get("Review.Flag", "")
                            or row.get("Review.Flag", "").startswith("DO NOT ANALYZE") for row in rows))


if __name__ == "__main__":
    unittest.main()
