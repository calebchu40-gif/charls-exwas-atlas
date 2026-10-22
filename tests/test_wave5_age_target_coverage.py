import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_wave5_age_target_coverage import summarize_age_weights


class Wave5AgeTargetCoverageTests(unittest.TestCase):
    def test_age_domains_use_crosssection_and_weight_denominator(self):
        frame = pd.DataFrame({
            "crosssection": [1] * 10 + [1] * 12 + [0] * 5,
            "xrage": [44] * 10 + [52] * 12 + [47] * 5,
            "INDV_weight": [1.0] * 27,
            "INDV_weight_ad2": [2.0] * 27,
        })
        rows = summarize_age_weights(frame)
        weight1 = [r for r in rows if r["weight"] == "INDV_weight"]
        under45 = next(r for r in weight1 if r["age_band"] == "under_45")
        age50_54 = next(r for r in weight1 if r["age_band"] == "50_54")
        self.assertEqual(under45["unweighted_n"], 10)
        self.assertEqual(age50_54["unweighted_n"], 12)
        self.assertEqual(under45["weighted_percent_of_positive_weight_total"], 45.45)
        self.assertEqual(age50_54["weighted_percent_of_positive_weight_total"], 54.55)

    def test_cells_below_ten_are_suppressed(self):
        frame = pd.DataFrame({
            "crosssection": [1] * 6,
            "xrage": [48] * 6,
            "INDV_weight": [1.0] * 6,
            "INDV_weight_ad2": [1.0] * 6,
        })
        rows = summarize_age_weights(frame)
        age45_49 = next(r for r in rows if r["weight"] == "INDV_weight" and r["age_band"] == "45_49")
        self.assertTrue(age45_49["cell_suppressed_lt_10"])
        self.assertIsNone(age45_49["unweighted_n"])
        self.assertIsNone(age45_49["weighted_population_sum"])


if __name__ == "__main__":
    unittest.main()
