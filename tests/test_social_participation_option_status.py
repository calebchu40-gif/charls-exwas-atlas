import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
STATUS = (
    "official Codebook identifies selected activity/device option; respondent-level storage, "
    "unselected state, and eligible denominator are unresolved; no response-value labels assigned"
)


class SocialParticipationOptionStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/social_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.crosswalk = [row for row in csv.DictReader(handle)
                             if row.get("wave") in {"2011", "2013", "2015"}
                             and row.get("code", "").lower().startswith("da056")]
        with (ROOT / "audit/charls_atlas_candidate_fields_v0.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.audit = list(csv.DictReader(handle))
        cls.site = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))

    def test_option_identity_is_not_misrepresented_as_respondent_value_labels(self):
        self.assertEqual(len(self.crosswalk), 41)
        for row in self.crosswalk:
            self.assertEqual(row.get("value_labels"), "")
            self.assertIn("Codebook_extracted.txt", row.get("value_label_source", ""))
            if row.get("concept_id") == "social_participation":
                self.assertEqual(row.get("value_label_status"), STATUS)
                self.assertIn("do not infer no from absence", row.get("value_semantics", "").lower())

    def test_audit_and_public_e_shard_show_review_state_without_invented_values(self):
        for row in self.crosswalk:
            key = (row["wave"], row["code"].lower())
            audit = [item for item in self.audit
                     if (item["Source.Wave"], item["Variable.Name"].lower()) == key]
            site = [item for item in self.site
                    if (item["Source.Wave"], item["Variable.Name"].lower()) == key]
            self.assertTrue(audit, key)
            self.assertTrue(site, key)
            self.assertTrue(all(item["Value.Label.Review"] == row["value_label_status"] for item in audit), key)
            self.assertTrue(all(item["Value.Labels"] == "" for item in audit), key)
            self.assertTrue(all(item["Value.Label.Review"] == row["value_label_status"] for item in site), key)
            self.assertTrue(all(item["Value.Labels"] == "" for item in site), key)


if __name__ == "__main__":
    unittest.main()
