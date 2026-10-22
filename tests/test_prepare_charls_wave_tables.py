import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_charls_wave_tables import split_weights  # noqa: E402
from validate_prepared_wave_tables import get_match_rate_0_to_1  # noqa: E402


class SplitWeightsTests(unittest.TestCase):
    def test_merge_match_rate_is_a_zero_to_one_proportion_and_reads_legacy_name(self):
        self.assertEqual(get_match_rate_0_to_1({"match_rate_0_to_1": 0.789269}), 0.789269)
        self.assertEqual(get_match_rate_0_to_1({"match_pct_of_base_nonmissing": 0.990907}), 0.990907)
        self.assertIsNone(get_match_rate_0_to_1({"match_rate_0_to_1": None}))

    def test_wave2_sample_flags_follow_person_weights(self):
        frame = pd.DataFrame(
            {
                "ID": ["001", "002"],
                "householdID": ["h1", "h2"],
                "INDV_weight": [1.2, 1.3],
                "Blood_weight": [0.8, 0.9],
                "crosssection": [1, 0],
                "longitudinal": [0, 1],
                "HH_weight_ad1": [2.1, 2.2],
            }
        )

        qa = []
        parts = split_weights(frame, "2013", qa)
        person = next(item for item in parts if item[0] == "Weights_person")
        household = next(item for item in parts if item[0] == "Weights_household")

        self.assertEqual(
            list(person[2].columns),
            ["ID", "INDV_weight", "Blood_weight", "crosssection", "longitudinal"],
        )
        self.assertEqual(person[2]["crosssection"].tolist(), [1, 0])
        self.assertEqual(person[2]["longitudinal"].tolist(), [0, 1])
        self.assertEqual(list(household[2].columns), ["householdID", "HH_weight_ad1"])

    def test_conflicting_sample_flags_block_person_weight_table(self):
        frame = pd.DataFrame(
            {
                "ID": ["001", "001", "002"],
                "householdID": ["h1", "h1", "h2"],
                "INDV_weight": [1.2, 1.2, 1.3],
                "crosssection": [1, 0, 1],
                "longitudinal": [0, 1, 0],
                "HH_weight": [2.1, 2.1, 2.2],
            }
        )

        qa = []
        parts = split_weights(frame, "2013", qa)

        self.assertNotIn("Weights_person", [item[0] for item in parts])
        self.assertIn("Weights_household", [item[0] for item in parts])
        person_qa = next(item for item in qa if item["module"] == "Weights_person")
        self.assertIn('"crosssection": 1', person_qa["other_id_mismatch_counts"])

    def test_wave2_without_official_sample_flags_fails_closed(self):
        frame = pd.DataFrame(
            {"ID": ["001"], "INDV_weight": [1.2], "HH_weight": [2.1]}
        )

        with self.assertRaisesRegex(ValueError, "must include crosssection and longitudinal"):
            split_weights(frame, "2013", [])

    def test_identical_duplicate_rows_collapse_without_losing_flag(self):
        frame = pd.DataFrame(
            {
                "ID": ["001", "001", "002"],
                "INDV_weight": [1.2, 1.2, 1.3],
                "crosssection": [1, 1, 0],
                "longitudinal": [0, 0, 1],
            }
        )

        parts = split_weights(frame, "2013", [])
        person = next(item[2] for item in parts if item[0] == "Weights_person")

        self.assertEqual(person["ID"].tolist(), ["001", "002"])
        self.assertEqual(person["crosssection"].tolist(), [1, 0])


if __name__ == "__main__":
    unittest.main()
