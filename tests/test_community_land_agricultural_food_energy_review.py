import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = "audit/community_land_agricultural_food_energy_context_review_2026-10-24.md"
EXPECTED = {
    "community_land_use_profile": {
        "ja003_1": "km²", "ja003_2": "mu", "ja011": "mu", "ja013": "mu",
        "ja014": "mu", "ja029": "mu", "ja032": "mu", "ja033": "percent",
        "ja034": "Yuan/mu/year", "ja050": "mu/person",
    },
    "community_main_terrain": {"ja038": ""},
    "community_agricultural_mechanization": {"jj002": "percent", "jj003": "", "jj004": "Yuan/day"},
    "community_fertilizer_seed_inputs": {"jj006": "", "jj007": "Yuan/jin", "jj008": "Yuan/jin", "jj009": "Yuan/jin", "jj010": "Yuan/jin"},
    "community_food_prices": {"jj017": "Yuan/jin", "jj018": "Yuan/jin", "jj019": "Yuan/jin", "jj020": "Yuan/jin"},
    "community_household_energy_prices": {"jj021": "Yuan/m³", "jj022": "Yuan/bottle", "jj025": "Yuan/jin"},
    "community_major_crop_production": {
        **{f"jj001_{rank}{suffix}": unit for rank in range(1, 4) for suffix, unit in (("a", ""), ("b", "mu"), ("c", "jin/mu"), ("d", ""), ("e", "harvest seasons/year"), ("f", "harvest seasons/year (historical maximum)"))},
    },
    "community_household_amenity_penetration": {code: "percent of village households" for code in ("jb023", "jb024", "jb025", "jb026")},
}


class CommunityLandAgricultureMarketReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/community_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.rows = list(csv.DictReader(f))
        cls.site = json.loads((ROOT / "site-prototype/dist/community_exposures_v1.json").read_text(encoding="utf-8"))
        cls.by_id = {item["concept_id"]: item for item in cls.site}

    def test_all_added_fields_units_and_scope_are_preserved(self):
        for concept_id, expected in EXPECTED.items():
            rows = {r["code"].lower(): r for r in self.rows if r["concept_id"] == concept_id}
            fields = {f["code"].lower(): f for f in self.by_id[concept_id]["source_fields"]}
            self.assertEqual(set(rows), set(expected))
            self.assertEqual(set(fields), set(expected))
            for code, unit in expected.items():
                self.assertEqual(rows[code]["unit"], unit)
                self.assertEqual(fields[code]["unit"], unit)
                self.assertEqual(rows[code]["wave"], "2011")
                self.assertIn("analysis eligibility pending", rows[code]["mapping_status"])
                self.assertTrue(rows[code]["source_evidence"].startswith("CHARLS 2011 Community Questionnaire"))
        self.assertEqual(sum(map(len, EXPECTED.values())), 48)

    def test_ja012_conflict_is_excluded_and_documented(self):
        self.assertFalse(any(r["code"].lower() == "ja012" for r in self.rows))
        audit = (ROOT / AUDIT).read_text(encoding="utf-8")
        self.assertIn("paddy field", audit)
        self.assertIn("Irrigatable", audit)
        self.assertIn("not included", audit)

    def test_terrain_labels_and_jj003_route_are_explicit(self):
        terrain = self.by_id["community_main_terrain"]["source_fields"][0]
        self.assertEqual(terrain["value_labels"], "1=Plain; 2=Hill; 3=Mountainous Region; 4=Plateau; 5=Basin")
        self.assertIn("nominal", terrain["caveat"])
        mechanization = {f["code"].lower(): f for f in self.by_id["community_agricultural_mechanization"]["source_fields"]}
        self.assertEqual(mechanization["jj003"]["value_labels"], "1=Yes; 2=No")
        self.assertIn("No routes past", mechanization["jj003"]["caveat"])
        self.assertIn("asked only after JJ003=Yes", mechanization["jj004"]["caveat"])

    def test_price_and_input_notes_do_not_claim_personal_dose_or_consumption(self):
        for concept_id in ("community_fertilizer_seed_inputs", "community_food_prices", "community_household_energy_prices"):
            concept = self.by_id[concept_id]
            self.assertIn("community", concept["caveat"].lower())
            self.assertTrue(any(term in concept["caveat"].lower() for term in ("not", "does not")))
        all_rows = [r for r in self.rows if r["concept_id"] in EXPECTED]
        self.assertTrue(all("Freq." not in r["source_evidence"] for r in all_rows))

    def test_crop_ranks_units_and_measurement_types_remain_distinct(self):
        concept = self.by_id["community_major_crop_production"]
        self.assertIn("up to three major crops", concept["caveat"])
        by_code = {f["code"].lower(): f for f in concept["source_fields"]}
        for rank in range(1, 4):
            self.assertEqual(by_code[f"jj001_{rank}d"]["value_labels"], "1=Yes; 2=No")
            self.assertIn("not individual machinery contact", by_code[f"jj001_{rank}d"]["caveat"])
            self.assertIn("historical maximum", by_code[f"jj001_{rank}f"]["unit"])
            self.assertIn("crop rank", by_code[f"jj001_{rank}b"]["caveat"])

    def test_amenity_percentages_remain_community_level(self):
        concept = self.by_id["community_household_amenity_penetration"]
        self.assertIn("aggregate community percentages", concept["caveat"])
        for field in concept["source_fields"]:
            self.assertEqual(field["unit"], "percent of village households")
            self.assertIn("not confirmed ownership or use", field["caveat"])


if __name__ == "__main__":
    unittest.main()
