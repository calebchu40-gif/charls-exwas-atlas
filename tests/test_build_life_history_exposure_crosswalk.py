import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_life_history_exposure_crosswalk as builder  # noqa: E402


class LifeHistoryCrosswalkTests(unittest.TestCase):
    def test_codebook_codes_with_spacing_are_normalized(self):
        sample = """\f--- PAGE 2 ---
CHARLSCodeBook 1 RESIDENCE
• t003c_1_s11 : Why Moved out 1st Residence: Intellectual Youth
• t004_1_: Rural or Urban
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "codebook.txt"
            path.write_text(sample, encoding="utf-8")
            with patch.object(builder, "CODEBOOK", path):
                fields = builder.read_codebook_fields()
        self.assertEqual(fields[("RESIDENCE", "t003c_1_s11")], "Why Moved out 1st Residence: Intellectual Youth")
        self.assertIn(("RESIDENCE", "t004_1_"), fields)

    def test_official_mapping_counts_and_repeated_episode_grouping(self):
        rows, groups = builder.build()
        self.assertEqual((len(groups), len(rows)), (40, 1029))
        self.assertEqual({role: sum(row["role"] == role for row in rows) for role in ("e", "p")}, {"e": 1001, "p": 28})
        by_concept = {}
        for row in rows:
            by_concept.setdefault(row["concept_id"], []).append(row)
        self.assertEqual(len(by_concept["life_history_residential_transition_reasons"]), 325)
        self.assertEqual(len(by_concept["life_history_residential_urbanicity"]), 25)
        self.assertEqual(len(by_concept["life_history_parental_divorce"]), 3)
        self.assertEqual(len(by_concept["life_history_famine_displacement"]), 1)
        self.assertEqual(len(by_concept["life_history_famine_flight_policy"]), 1)
        self.assertEqual(len(by_concept["life_history_famine_family_mortality"]), 2)
        self.assertEqual(len(by_concept["life_history_famine_family_reproductive_consequences"]), 6)
        option5 = next(row for row in by_concept["life_history_famine_family_reproductive_consequences"] if row["code"] == "c8s5")
        self.assertIn("Chinese says 'abandoning an infant'", option5["caveat"])
        self.assertEqual(len(by_concept["life_history_guardian_depressive_symptoms"]), 12)
        self.assertEqual(len(by_concept["life_history_guardian_substance_behaviors"]), 16)
        self.assertEqual(len(by_concept["life_history_guardian_behavioral_adversity"]), 14)
        self.assertEqual(len(by_concept["life_history_guardian_physical_mental_health"]), 6)
        h16 = [row for row in by_concept["life_history_guardian_behavioral_adversity"] if row["code"] in {"h16_a", "h16_b"}]
        self.assertTrue(all("option sets differ" in row["value_labels"] for row in h16))
        self.assertEqual(len(by_concept["life_history_sibling_death_before_age6"]), 61)
        self.assertEqual(len(by_concept["life_history_sibling_family_structure"]), 72)
        self.assertEqual(len(by_concept["life_history_sibling_party_membership"]), 26)
        self.assertEqual(len(by_concept["life_history_sibling_ethnic_context"]), 41)
        self.assertEqual(len(by_concept["life_history_sibling_sent_down_experience"]), 26)
        self.assertEqual(len(by_concept["life_history_sibling_death_after_age6"]), 15)
        self.assertEqual(len(by_concept["life_history_parental_loss"]), 6)
        self.assertEqual(len(by_concept["life_history_parental_remarriage_stepfamily"]), 24)
        self.assertEqual(len(by_concept["life_history_nonbiological_parent_education"]), 4)
        self.assertEqual(len(by_concept["life_history_parental_party_membership_context"]), 9)
        self.assertEqual(len(by_concept["life_history_parental_minority_ethnicity_context"]), 9)
        self.assertEqual(len(by_concept["life_history_parental_minority_group_context"]), 9)
        self.assertEqual(len(by_concept["life_history_parental_religious_context"]), 9)
        self.assertTrue(all("Chinese repeats A4a" in row["caveat"] for row in by_concept["life_history_parental_religious_context"]))
        self.assertEqual(len([row for row in by_concept["life_history_guardian_employment_context"] if row["code"].startswith("c1_")]), 2)
        self.assertEqual(len([row for row in by_concept["life_history_guardian_employment_context"] if row["code"].startswith("c2_")]), 4)
        self.assertEqual(len(by_concept["life_history_childhood_guardian_occupation"]), 2)
        self.assertTrue(all("blank is not No" in row["caveat"] for row in by_concept["life_history_guardian_employment_context"]))
        self.assertEqual(len(by_concept["life_history_historical_family_class_background"]), 189)
        self.assertEqual({row["module"] for row in by_concept["life_history_historical_family_class_background"]}, {"WEALTHHISTORY"})
        self.assertTrue(all(row["code"] != "c5" for row in by_concept["life_history_historical_family_class_background"]))
        self.assertNotIn("b4_1_1_", {row["code"] for row in rows})
        self.assertFalse(any(row["code"].startswith("b2_4") for row in rows))
        self.assertEqual(len({(row["module"], row["code"]) for row in rows}), len(rows))
        self.assertFalse(any("OBS:" in " ".join(row.values()) for row in rows))

    def test_sibling_module_inventory_has_explicit_disposition_for_every_codebook_field(self):
        rows, _ = builder.build()
        coverage = builder.build_sibling_module_coverage(rows)
        self.assertEqual(len(coverage), 271)
        self.assertEqual(sum(row["disposition"] == "mapped_candidate" for row in coverage), 241)
        self.assertEqual(sum(row["disposition"] != "mapped_candidate" for row in coverage), 30)
        self.assertEqual({row["disposition"] for row in coverage if row["code"].startswith("b4_4_")}, {"deferred_relative_status"})
        self.assertEqual({row["disposition"] for row in coverage if row["code"].startswith("b4_5_")}, {"deferred_relative_attainment"})

    def test_parent_module_inventory_has_explicit_disposition_for_every_codebook_field(self):
        rows, _ = builder.build()
        coverage = builder.build_parent_module_coverage(rows)
        self.assertEqual(len(coverage), 47)
        self.assertEqual(sum(row["disposition"] == "mapped_candidate" for row in coverage), 39)
        self.assertEqual(sum(row["disposition"] != "mapped_candidate" for row in coverage), 8)

    def test_historical_family_class_fields_map_exhaustively_without_frequencies(self):
        rows, _ = builder.build()
        coverage = builder.build_historical_family_class_coverage(rows)
        self.assertEqual(len(coverage), 189)
        self.assertTrue(all(row["disposition"] == "mapped_candidate" for row in coverage))
        self.assertEqual(len({row["code"] for row in coverage}), 189)

    def test_parent_social_context_inventory_maps_all_selector_fields_and_retains_translation_caveat(self):
        rows, _ = builder.build()
        coverage = builder.build_parent_social_context_coverage(rows)
        self.assertEqual(len(coverage), 36)
        self.assertEqual({row["disposition"] for row in coverage}, {"mapped_candidate"})
        self.assertEqual(len({row["code"] for row in coverage}), 36)
        religion = [row for row in coverage if row["concept_id"] == "life_history_parental_religious_context"]
        self.assertEqual(len(religion), 9)
        self.assertTrue(all("Chinese repeats A4a" in row["rationale"] for row in religion))

    def test_parent_employment_inventory_keeps_routes_and_excludes_free_text_fields(self):
        rows, _ = builder.build()
        coverage = builder.build_parent_employment_coverage(rows)
        self.assertEqual(len(coverage), 8)
        self.assertEqual(len({row["code"] for row in coverage}), 8)
        self.assertEqual({row["disposition"] for row in coverage}, {"mapped_candidate"})
        codes = {row["code"] for row in coverage}
        self.assertNotIn("c1_a2_1", codes)
        self.assertNotIn("c1_b2_1", codes)
        unemployment = [row for row in coverage if row["code"].startswith("c2_")]
        self.assertEqual({row["code"] for row in unemployment}, {"c2_a", "c2_a_1", "c2_b", "c2_b_1"})


if __name__ == "__main__":
    unittest.main()
