import csv
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SupplementalHealthInsuranceMappingTests(unittest.TestCase):
    def test_candidate_slots_match_wave_specific_sources(self):
        with (ROOT / "audit/healthcare_access_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = [row for row in csv.DictReader(handle) if row["concept_id"] == "health_insurance_supplemental_coverage"]
        self.assertEqual(len(rows), 17)
        self.assertEqual(
            {wave: {row["code"] for row in rows if row["wave"] == wave} for wave in ("2011", "2013", "2018")},
            {
                "2011": {f"ea002_{i}_" for i in range(1, 9)},
                "2013": {f"ea002_{i}_" for i in (1, 2, 3, 4, 5, 6, 9, 10)},
                "2018": {"ea002"},
            },
        )

    def test_official_codebooks_contain_codes_and_labels_only_are_exposed(self):
        rows = []
        with (ROOT / "audit/healthcare_access_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = [row for row in csv.DictReader(handle) if row["concept_id"] == "health_insurance_supplemental_coverage"]
        for row in rows:
            source = ROOT / f"sources_official/CHARLS_{row['wave']}_Codebook_extracted.txt"
            text = source.read_text(encoding="utf-8", errors="replace").casefold().replace("\x00", "")
            normalized_code = re.sub(r"[^a-z0-9]", "", row["code"].casefold())
            normalized_text = re.sub(r"[^a-z0-9]", "", text)
            self.assertTrue(normalized_code in normalized_text, msg=f"{row['wave']} {row['code']} absent from Codebook")
            self.assertEqual(row["value_labels"], "1=Yes; 2=No")
            self.assertNotIn("freq", row["value_labels"].casefold())
        self.assertTrue(all("plan-slot" in row["mapping_status"] for row in rows))
        self.assertTrue(any("structural" in row["value_semantics"].casefold() for row in rows))

    def test_exit_interview_is_not_included_as_respondent_exposure(self):
        with (ROOT / "audit/healthcare_access_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertFalse(any(row["code"].startswith("exea002") for row in rows))


if __name__ == "__main__":
    unittest.main()
