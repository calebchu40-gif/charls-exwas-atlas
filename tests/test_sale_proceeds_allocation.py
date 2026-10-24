import csv
import re
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
sys.path.insert(0, str(ROOT / "scripts"))


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class SaleProceedsAllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.crosswalk = rows(AUDIT / "household_sale_proceeds_allocation_crosswalk_v1.csv")
        cls.overrides = rows(AUDIT / "catalog_role_override_review_v1.csv")
        cls.catalog = rows(AUDIT / "charls_atlas_candidate_fields_v0.csv")

    def test_numeric_percentages_are_separate_locked_candidate_fields(self):
        amounts = [r for r in self.crosswalk if r["concept_id"] == "house_sale_proceeds_allocation_percent_2013_2015"]
        self.assertEqual(len(amounts), 54)
        self.assertEqual({w: sum(r["wave"] == w for r in amounts) for w in ("2013", "2015")}, {"2013": 27, "2015": 27})
        self.assertTrue(all(re.fullmatch(r"ha026_w2_5[a-hj]_(1|2|25)_", r["code"]) for r in amounts))
        self.assertTrue(all(r["unit"].startswith("% of proceeds") for r in amounts))
        self.assertTrue(all("DO NOT ANALYZE" in r["mapping_status"] for r in amounts))
        self.assertTrue(all(not r["value_labels"] for r in amounts))
        self.assertFalse(any("OBS" in str(r.values()) or "Mean" in str(r.values()) for r in amounts))
        e_catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog if r["epcf"] == "e"}
        for r in amounts:
            self.assertIn((r["wave"], r["code"]), e_catalog)
            self.assertIn("DO NOT ANALYZE", e_catalog[(r["wave"], r["code"])]["Review.Flag"])

    def test_option_selectors_and_other_use_text_are_metadata_only(self):
        selectors = [r for r in self.crosswalk if r["concept_id"] == "house_sale_proceeds_allocation_category_2013_2015"]
        self.assertEqual(len(selectors), 54)
        self.assertTrue(all(not r["value_labels"] for r in selectors))
        override_map = {(r["wave"], r["code"]): r for r in self.overrides}
        for r in selectors:
            override = override_map[(r["wave"], r["code"])]
            self.assertEqual(override["keep_role"], "c")
            self.assertEqual(override["metadata_type"], "sale_proceeds_selector_metadata")
        c_catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog if r["epcf"] == "c"}
        for r in selectors:
            self.assertIn((r["wave"], r["code"]), c_catalog)
        text_fields = [r for r in override_map.values() if r["metadata_type"] == "sale_proceeds_other_use_text"]
        self.assertEqual(len(text_fields), 4)
        self.assertTrue(all(r["keep_role"] == "c" for r in text_fields))

    def test_private_storage_qa_maps_slots_and_never_emits_raw_values(self):
        from audit_household_sale_proceeds_storage import planned_columns, summarize_response

        plan = planned_columns()
        self.assertEqual(set(plan), {"2013", "2015"})
        self.assertEqual(len(plan["2013"]), 57)
        self.assertEqual(len(plan["2015"]), 57)
        summary = summarize_response(
            pd.Series(["25", "", "999", "text"]),
            pd.Series(["1", "", "1", ""]),
            pd.Series(["3", "3", "2", ""]),
        )
        self.assertTrue(summary["amount_present"])
        self.assertFalse(summary["all_nonblank_amounts_numeric"])
        self.assertFalse(summary["all_numeric_amounts_within_0_100"])
        self.assertFalse(summary["selector_amount_linkage_consistent"])
        self.assertFalse(summary["selector_without_amount_observed"])
        self.assertTrue(summary["amount_without_selector_observed"])
        self.assertFalse(summary["amount_only_when_status_sold"])
        self.assertNotIn("raw_values", summary)
        self.assertNotIn("ids", summary)


if __name__ == "__main__":
    unittest.main()
