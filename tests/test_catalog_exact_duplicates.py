import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ExactCatalogDuplicateTests(unittest.TestCase):
    def test_candidate_and_master_catalogs_have_no_exact_duplicate_rows(self):
        paths = (
            ROOT / "audit/charls_atlas_candidate_fields_v0.csv",
            ROOT / "audit/charls_atlas_candidate_fields_v0.json",
            ROOT / "site-prototype/dist/catalog.json",
        )
        for path in paths:
            with self.subTest(path=path.name):
                if path.suffix == ".csv":
                    with path.open(encoding="utf-8-sig", newline="") as stream:
                        rows = list(csv.DictReader(stream))
                else:
                    rows = json.loads(path.read_text(encoding="utf-8"))
                signatures = [json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for row in rows]
                self.assertEqual(len(signatures), len(set(signatures)))


if __name__ == "__main__":
    unittest.main()
