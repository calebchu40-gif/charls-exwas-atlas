import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HukouOverlapReviewTests(unittest.TestCase):
    def test_exact_overlaps_remain_c_metadata_and_keep_official_provenance(self):
        with (ROOT / "audit/hukou_c_overlap_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            reviewed = list(csv.DictReader(f))
        self.assertEqual(len(reviewed), 20)
        self.assertEqual(len({(r["wave"], r["code"], r["module"]) for r in reviewed}), 20)
        self.assertTrue(all(r["official_sources"] and "sources_official/" in r["official_sources"] for r in reviewed))
        catalog = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        keyset = {(r["wave"], r["code"].lower(), r["module"]) for r in reviewed}
        matched = [r for r in catalog if (r["Source.Wave"], r["Variable.Name"].lower(), r["Data.File.Name"]) in keyset]
        self.assertEqual(len(matched), 20)
        self.assertTrue(all(r["epcf"] == "c" for r in matched))
        self.assertTrue(all(r["Value.Label.Review"] != "not yet reviewed" for r in matched))
        self.assertTrue(all("estimand-specific" in r["Candidate.Status"] for r in matched))
        self.assertTrue(all(not r["Value.Labels"] for r in matched if r["Unit"] in ("", "calendar year", "calendar month")))
        self.assertTrue(all("automatic model recommendation" not in r["Review.Flag"] for r in matched))


if __name__ == "__main__":
    unittest.main()
