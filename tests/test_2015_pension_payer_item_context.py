import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class Pension2015PayerContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv(ROOT / "audit/pension_exposure_variable_mapping_v1.csv")
        cls.rows = [r for r in cls.rows if r["wave"] == "2015"]

    def by_code(self, code):
        return next(r for r in self.rows if r["code"].lower() == code.lower())

    def test_fn074_other_person_slot_is_not_free_text_or_generic_payer(self):
        rows = [r for r in self.rows if r["code"].lower().startswith("fn074_w3_pay_")]
        self.assertEqual(len(rows), 3)
        self.assertTrue(all("fn074_supplementary_payer_other_person_option" in r["concept_id"] for r in rows))
        self.assertTrue(all("option 28" in r["caveat"] and "free-text" in r["caveat"] for r in rows))
        self.assertTrue(all("printed page 178" in r["mapping_status"] for r in rows))

    def test_fn076_option_slots_remain_distinct_and_plan_specific(self):
        rows = [r for r in self.rows if r["code"].lower().startswith("fn076_w3_")]
        self.assertEqual(len(rows), 84)
        self.assertEqual(len({r["concept_id"] for r in rows}), 3)
        self.assertTrue(all("fn076_contribution_payer" in r["concept_id"] for r in rows))
        self.assertTrue(all("FN075_W3_5" in r["caveat"] and "FN072_W3_5" in r["caveat"] for r in rows))
        self.assertTrue(all("printed page 181" in r["mapping_status"] for r in rows))

    def test_fn075_payer_means_annual_contribution_after_supplementary_repayment(self):
        rows = [r for r in self.rows if r["code"].lower().startswith("fn075_w3_5_")]
        self.assertEqual(len(rows), 3)
        self.assertTrue(all("annual_contribution_payer" in r["concept_id"] for r in rows))
        self.assertTrue(all("not the payer of the earlier supplementary amount" in r["caveat"] for r in rows))
        self.assertTrue(all("FN074/FN076" in r["caveat"] for r in rows))

    def test_prior_year_fn072_payer_is_not_merged_with_other_contexts(self):
        rows = [r for r in self.rows if r["code"].lower().startswith("fn072_w3_5_")]
        self.assertEqual(len(rows), 84)
        self.assertTrue(all(r["concept_id"].endswith("_last_year") for r in rows))
        self.assertNotEqual(self.by_code("fn072_w3_5_1_s1")["concept_id"], self.by_code("fn076_w3_1_s1")["concept_id"])
        self.assertNotEqual(self.by_code("fn072_w3_5_1_s1")["concept_id"], self.by_code("fn075_w3_5_1_")["concept_id"])


if __name__ == "__main__":
    unittest.main()
