import csv
import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


class MaritalHistoryEventDateReviewTests(unittest.TestCase):
    def test_wave_specific_exposure_mapping_and_no_observation_boundary(self):
        crosswalk = pd.read_csv(ROOT / "audit/marital_history_exposure_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
        keys = {(r.wave, r.code.lower()) for r in crosswalk.itertuples(index=False)}
        self.assertTrue({("2011", "be007"), ("2011", "be008"), ("2013", "be009_1"), ("2013", "be009_2")}.issubset(keys))
        self.assertFalse({("2015", "be009_1"), ("2015", "be009_2")} & keys)
        month = crosswalk[(crosswalk.wave == "2013") & (crosswalk.code == "be009_2")].iloc[0]
        self.assertIn("0=Do not remember", month.value_labels)
        self.assertIn("official questionnaire response categories reviewed", month.value_label_status)
        self.assertNotIn("25.19", month.value_labels)
        e = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))
        mapped_e = [r for r in e if (r.get("Source.Wave"), r.get("Variable.Name", "").lower()) in {("2011", "be007"), ("2011", "be008"), ("2013", "be009_1"), ("2013", "be009_2")}]
        self.assertEqual(len(mapped_e), 4)
        self.assertTrue(all("not yet reviewed" not in r["Value.Label.Review"] for r in mapped_e))

        with (ROOT / "audit/marriage_date_2015_no_observation_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            no_observation = list(csv.DictReader(f))
        self.assertEqual({r["code"] for r in no_observation}, {"be009_1", "be009_2"})
        self.assertTrue(all("No Observations" in r["review_status"] for r in no_observation))
        c = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        wave3 = [r for r in c if r.get("Source.Wave") == "2015" and r.get("Variable.Name", "").lower() in {"be009_1", "be009_2"}]
        self.assertEqual(len(wave3), 2)
        self.assertTrue(all(r["epcf"] == "c" and "No Observations" in r["Value.Label.Review"] for r in wave3))

    def test_four_source_reviewed_c_rows_are_explicit_e_c_overlaps(self):
        with (ROOT / "audit/marital_history_c_overlap_review_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            audit = list(csv.DictReader(f))
        self.assertEqual(len(audit), 4)
        c = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        keys = {(x["wave"], x["code"].lower()) for x in audit}
        matched = [r for r in c if (r["Source.Wave"], r["Variable.Name"].lower()) in keys]
        self.assertEqual(len(matched), 4)
        self.assertTrue(all("marital-history exposure overlap" in r["subcategory"] for r in matched))
        self.assertTrue(all("not adjust for itself" in r["Candidate.Status"] for r in matched))


if __name__ == "__main__":
    unittest.main()
