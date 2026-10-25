import unittest
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_2011_chronic_treatment_storage import audit_frame


class ChronicTreatmentStorageAuditTests(unittest.TestCase):
    def test_expected_option_codes_and_exclusive_none_pass(self):
        frame = pd.DataFrame({
            f"da010_{disease}_s{option}": [
                option if row == int(option) - 1 else None for row in range(4)
            ]
            for disease in ("2", "5", "6", "7", "9", "10", "12", "13")
            for option in ("1", "2", "3", "4")
        })
        for disease in ("2", "5", "6", "7", "9", "10", "12", "13"):
            frame[f"da007_{disease}_"] = [1, 1, 1, 1]
        rows = audit_frame(frame)
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["all_fields_observed"] for row in rows))
        self.assertTrue(all(row["all_nonmissing_values_match_option_index"] for row in rows))
        self.assertTrue(all(row["none_option_never_cooccurs_with_treatment_option"] for row in rows))
        self.assertFalse(any(row["treatment_observed_when_doctor_diagnosis_response_is_no"] for row in rows))

    def test_code_mismatch_and_none_overlap_fail_closed(self):
        values = {f"da010_{disease}_s{option}": [None, None] for disease in ("2", "5", "6", "7", "9", "10", "12", "13") for option in ("1", "2", "3", "4")}
        values.update({f"da007_{disease}_": [1, 2] for disease in ("2", "5", "6", "7", "9", "10", "12", "13")})
        values["da010_2_s1"] = [1, None]
        values["da010_2_s2"] = [None, 99]
        values["da010_2_s4"] = [4, 4]
        rows = {row["disease_index"]: row for row in audit_frame(pd.DataFrame(values))}
        self.assertFalse(rows["2"]["all_nonmissing_values_match_option_index"])
        self.assertFalse(rows["2"]["none_option_never_cooccurs_with_treatment_option"])
        self.assertFalse(rows["5"]["all_fields_observed"])
        self.assertTrue(rows["2"]["treatment_observed_when_doctor_diagnosis_response_is_no"])


if __name__ == "__main__":
    unittest.main()
