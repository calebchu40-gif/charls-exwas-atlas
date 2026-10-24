import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from adjust_exwas_pvalues import adjust_pvalues  # noqa: E402


class ExwasPValueAdjustmentTests(unittest.TestCase):
    def test_bonferroni_and_by_match_reference_family(self):
        adjusted = adjust_pvalues([0.01, 0.04, 0.03])
        self.assertEqual(adjusted["p_bonferroni"], [0.03, 0.12, 0.09])
        expected_by = [0.055, 0.07333333333333333, 0.07333333333333333]
        for observed, expected in zip(adjusted["q_value_by"], expected_by):
            self.assertTrue(math.isclose(observed, expected, rel_tol=1e-12, abs_tol=1e-12))

    def test_adjustments_preserve_input_order_and_cap_at_one(self):
        adjusted = adjust_pvalues([1.0, 0.0, 0.5, 0.5])
        self.assertEqual(adjusted["p_bonferroni"], [1.0, 0.0, 1.0, 1.0])
        self.assertEqual(adjusted["q_value_by"][1], 0.0)
        self.assertTrue(all(0 <= value <= 1 for value in adjusted["q_value_by"]))
        self.assertEqual(adjust_pvalues([]), {"p_bonferroni": [], "q_value_by": []})

    def test_unestimable_predeclared_hypothesis_still_counts_in_family(self):
        adjusted = adjust_pvalues([0.01, None, 0.04])
        self.assertEqual(adjusted["p_bonferroni"], [0.03, None, 0.12])
        self.assertTrue(math.isclose(adjusted["q_value_by"][0], 0.055, rel_tol=1e-12))
        self.assertIsNone(adjusted["q_value_by"][1])
        self.assertTrue(math.isclose(adjusted["q_value_by"][2], 0.11, rel_tol=1e-12))

    def test_nonfinite_or_out_of_range_values_fail_closed(self):
        for values in ([float("nan")], [float("inf")], [-0.001], [1.001]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                adjust_pvalues(values)


if __name__ == "__main__":
    unittest.main()
