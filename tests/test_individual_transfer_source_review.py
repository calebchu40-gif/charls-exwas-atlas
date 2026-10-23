import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRANSFER_CODES = {
    "2011": {f"ga003s{i}" for i in range(1, 11)},
    "2013": {f"ga003s{i}" for i in range(1, 11)},
    "2015": {f"ga003s{i}" for i in range(1, 11)},
    "2018": {f"ga003_w4_s{i}" for i in range(1, 11)},
    "2020": {f"ga005_s{i}" for i in range(1, 11)},
}


class IndividualTransferSourceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/charls_atlas_candidate_fields_v0.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.fields = list(csv.DictReader(handle))
        with (ROOT / "audit/individual_transfer_income_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.crosswalk = list(csv.DictReader(handle))
        cls.catalog = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))

    def test_fifty_person_level_fields_are_wave_reviewed(self):
        rows = [r for r in self.fields if r.get("Candidate.Status") == "individual transfer-income source candidate; retain person-level source and wave-specific response coding"]
        self.assertEqual(len(rows), 50)
        for wave, codes in TRANSFER_CODES.items():
            observed = {r["Variable.Name"].lower() for r in rows if r["Source.Wave"] == wave}
            self.assertEqual(observed, codes)

    def test_early_wave_labels_do_not_infer_no_for_unselected_slots(self):
        rows = [r for r in self.catalog if r.get("Source.Wave") in {"2011", "2013", "2015"} and r.get("Variable.Name", "").lower() in set.union(*[TRANSFER_CODES[w] for w in ("2011", "2013", "2015")])]
        self.assertEqual(len(rows), 30)
        for row in rows:
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("unselected storage", row["Value.Label.Review"].lower())
            self.assertIn("Do not infer No from blank", row["Harmonization.Status"])

    def test_2018_and_2020_use_option_specific_yes_codes(self):
        rows = [r for r in self.catalog if r.get("Source.Wave") in {"2018", "2020"} and r.get("Candidate.Status") == "individual transfer-income source candidate; retain person-level source and wave-specific response coding"]
        self.assertEqual(len(rows), 20)
        for row in rows:
            option = row["Variable.Name"].lower().rsplit("s", 1)[1]
            self.assertEqual(row["Value.Labels"], f"0=No; {option}=Yes")
            self.assertNotRegex(row["Value.Labels"], r"\d{1,3}(?:,\d{3})+")

    def test_mapping_retains_all_wave_specific_sources(self):
        rows = [r for r in self.crosswalk if r.get("concept_id") == "individual_transfer_income_source_receipt"]
        self.assertEqual(len(rows), 50)
        for row in rows:
            self.assertIn(f"CHARLS_{row['wave']}_Codebook_extracted.txt", row["value_label_source"])


if __name__ == "__main__":
    unittest.main()
