import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CatalogCrosswalkStatusPropagationTests(unittest.TestCase):
    def test_functional_source_mappings_are_not_left_as_automated_hits(self):
        rows = json.loads((ROOT / "site-prototype/dist/catalog_p.json").read_text(encoding="utf-8"))
        mapping_sources = {
            "audit/functional_concept_variable_mapping_v1.csv",
            "audit/disability_history_crosswalk_v1.csv",
            "audit/health_work_limitation_crosswalk_v1.csv",
        }
        reviewed = [row for row in rows
                    if row.get("category") == "physical function"
                    and row.get("Concept.Mapping.Source") in mapping_sources]
        self.assertGreaterEqual(len(reviewed), 100)
        stale = [row for row in reviewed
                 if row.get("Candidate.Status", "").lower().startswith(("automated discovery", "automated keyword discovery"))]
        self.assertEqual(stale, [])
        self.assertTrue(all("approved test variable" in row.get("Review.Flag", "")
                            or "not analytic inclusion" in row.get("Review.Flag", "") for row in reviewed))


if __name__ == "__main__":
    unittest.main()
