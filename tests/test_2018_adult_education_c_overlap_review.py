import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AdultEducationCovariateOverlapTests(unittest.TestCase):
    def test_two_wave4_fields_keep_years_route_and_estimand_caveat(self):
        with (ROOT / "audit/adult_education_c_overlap_review_2018_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            audit = list(csv.DictReader(f))
        self.assertEqual({r["code"] for r in audit}, {"bd008_w2_1", "bd008_w4_1"})
        catalog = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        rows = [r for r in catalog if r.get("Source.Wave") == "2018" and r.get("Variable.Name", "").lower() in {"bd008_w2_1", "bd008_w4_1"}]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all("not adjust for itself" in r["Candidate.Status"] for r in rows))
        self.assertTrue(all(r["epcf"] == "c" and r["Unit"] == "years" for r in rows))
        self.assertTrue(all(not r["Value.Labels"] for r in rows))
        self.assertTrue(all("None" in r["Review.Flag"] and "structural skips are not zero" in r["Review.Flag"] for r in rows))
        by_code = {r["Variable.Name"].lower(): r for r in rows}
        self.assertIn("total years", by_code["bd008_w2_1"]["Review.Flag"])
        self.assertIn("since ZIWTime", by_code["bd008_w4_1"]["Review.Flag"])


if __name__ == "__main__": unittest.main()
