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
        self.assertEqual((len(groups), len(rows)), (118, 3300))
        self.assertEqual({role: sum(row["role"] == role for row in rows) for role in ("e", "p")}, {"e": 3254, "p": 46})
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
        self.assertEqual(len(by_concept["life_history_childhood_romantic_relationship"]), 2)
        self.assertEqual(len(by_concept["life_history_childhood_police_custody_and_charge"]), 2)
        justice = by_concept["life_history_childhood_police_custody_and_charge"]
        self.assertTrue(all("not proof of conviction or guilt" in row["caveat"] for row in justice))
        self.assertFalse(any("OBS:" in " ".join(row.values()) for row in justice))
        self.assertEqual(len(by_concept["life_history_residential_episode_timing"]), 250)
        self.assertEqual(len(by_concept["life_history_between_residence_migration_reasons"]), 169)
        self.assertTrue(all("not T003c reasons" in row["caveat"] for row in by_concept["life_history_between_residence_migration_reasons"]))
        self.assertEqual(len(by_concept["life_history_inheritance_history"]), 72)
        self.assertEqual(len(by_concept["life_history_family_political_death_context"]), 9)
        self.assertEqual(len(by_concept["life_history_family_rightist_label_context"]), 10)
        self.assertEqual(len(by_concept["life_history_red_guard_participation"]), 1)
        self.assertEqual(len(by_concept["life_history_land_expropriation_history"]), 93)
        self.assertEqual(len(by_concept["life_history_home_demolition_history"]), 58)
        self.assertFalse(any("OBS:" in " ".join(row.values()) for key in ("life_history_inheritance_history", "life_history_land_expropriation_history", "life_history_home_demolition_history") for row in by_concept[key]))
        health_counts = {
            "life_history_menarche_timing": 1,
            "life_history_adult_injury_disability": 5,
            "life_history_ill_health_work_consequences": 7,
            "life_history_adult_health_burden": 4,
            "life_history_childhood_vaccination": 1,
            "life_history_usual_source_of_care": 9,
            "life_history_adult_blood_pressure_screening": 2,
            "life_history_adult_blood_test": 2,
            "life_history_breast_screening": 2,
            "life_history_prostate_screening": 2,
            "life_history_vision_screening": 2,
            "life_history_dental_screening": 2,
            "life_history_physical_activity_increase_periods": 8,
            "life_history_diet_change_periods": 8,
            "life_history_smoking_cessation_periods": 8,
            "life_history_alcohol_reduction_periods": 8,
            "life_history_medical_insurance_history": 2,
        }
        for concept, count in health_counts.items():
            self.assertEqual(len(by_concept[concept]), count, concept)
        self.assertEqual(len(by_concept["life_history_sample_vital_status"]), 1)
        self.assertEqual(by_concept["life_history_sample_vital_status"][0]["code"], "died")
        self.assertIn("population mortality rate", by_concept["life_history_sample_vital_status"][0]["caveat"])
        education_counts = {
            "life_history_education_level_history": 12,
            "life_history_literacy": 1,
            "life_history_cultural_revolution_school_disruption": 7,
            "life_history_schooling_interruption": 9,
            "life_history_school_dormitory_experience": 4,
            "life_history_primary_school_attainment": 5,
            "life_history_primary_school_interruption_detail": 14,
            "life_history_middle_school_attainment": 8,
            "life_history_middle_school_interruption_detail": 14,
            "life_history_high_school_attendance_intensity": 3,
            "life_history_high_school_interruption_detail": 14,
            "life_history_high_school_completion_and_exam_pathway": 8,
            "life_history_vocational_education_pathway": 34,
            "life_history_vocational_school_interruption_detail": 14,
            "life_history_three_year_college_pathway": 40,
            "life_history_three_year_college_interruption_detail": 14,
            "life_history_four_year_college_pathway": 51,
            "life_history_four_year_college_interruption_detail": 14,
            "life_history_masters_education_pathway": 20,
            "life_history_masters_education_interruption_detail": 14,
            "life_history_phd_education_pathway": 18,
            "life_history_phd_education_interruption_detail": 14,
            "life_history_primary_education_continuation_barriers": 13,
            "life_history_middle_education_continuation_barriers": 13,
            "life_history_high_education_continuation_barriers": 13,
            "life_history_adult_education_types": 9,
            "life_history_adult_literacy_class": 4,
            "life_history_adult_evening_class": 16,
            "life_history_career_training_history": 121,
            "life_history_accelerated_education_course": 4,
            "life_history_radio_television_university": 11,
            "life_history_correspondence_education": 16,
            "life_history_self_study_examination": 16,
            "life_history_other_adult_education": 25,
            "life_history_skill_certificate_indicator": 1,
            "life_history_education_gap_activity_context": 242,
            "life_history_education_gap_without_other_schooling": 20,
            "life_history_early_education_episode_counts": 4,
            "life_history_education_episode_timing": 240,
            "life_history_status_at_age_16": 13,
            "life_history_repeated_job_type": 19,
            "life_history_repeated_job_timing": 171,
            "life_history_lifetime_work_participation": 1,
            "life_history_lifetime_nonwork_reason": 1,
            "life_history_repeated_employer_type": 19,
            "life_history_repeated_firm_ownership": 15,
            "life_history_repeated_public_sector_staff_status": 13,
            "life_history_repeated_agricultural_work_intensity": 72,
            "life_history_repeated_employee_work_intensity": 72,
            "life_history_repeated_self_employed_work_intensity": 63,
        }
        for concept, count in education_counts.items():
            self.assertEqual(len(by_concept[concept]), count, concept)
        self.assertTrue(all("at least a year" in " ".join(r.values()) for concept in (
            "life_history_physical_activity_increase_periods", "life_history_diet_change_periods",
            "life_history_smoking_cessation_periods", "life_history_alcohol_reduction_periods") for r in by_concept[concept]))
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

    def test_work_history_lifetime_work_items_and_route_checks_are_separated(self):
        rows, _ = builder.build()
        ledger = builder.build_work_history_coverage(rows)
        by_code = {row["code"]: row for row in ledger}
        self.assertEqual(by_code["f_1"]["concept_id"], "life_history_lifetime_work_participation")
        self.assertEqual(by_code["f_1_2"]["concept_id"], "life_history_lifetime_nonwork_reason")
        self.assertEqual(by_code["f_1_0"]["disposition"], "excluded_route_quality_metadata")
        self.assertEqual(by_code["f_1_1"]["disposition"], "excluded_route_quality_metadata")
        self.assertEqual(sum(row["disposition"] == "mapped_candidate" for row in ledger), 459)
        self.assertEqual(sum(row["disposition"] == "deferred_source_review" for row in ledger), 1540)
        self.assertEqual(sum(row["concept_id"] == "life_history_repeated_employer_type" for row in ledger), 19)
        self.assertEqual(sum(row["concept_id"] == "life_history_repeated_firm_ownership" for row in ledger), 15)
        self.assertEqual(sum(row["concept_id"] == "life_history_repeated_public_sector_staff_status" for row in ledger), 13)
        self.assertEqual(sum(row["concept_id"] == "life_history_repeated_agricultural_work_intensity" for row in ledger), 72)
        self.assertEqual(sum(row["concept_id"] == "life_history_repeated_employee_work_intensity" for row in ledger), 72)
        self.assertEqual(sum(row["concept_id"] == "life_history_repeated_self_employed_work_intensity" for row in ledger), 63)

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

    def test_sensitive_history_inventory_is_metadata_only_and_preserves_skip_routes(self):
        rows, _ = builder.build()
        coverage = builder.build_sensitive_history_coverage(rows)
        self.assertEqual({row["code"] for row in coverage}, {"e7", "e8", "g1", "g2"})
        self.assertEqual({row["disposition"] for row in coverage}, {"mapped_metadata_only"})
        self.assertIn("blank E8 is not No", next(row["rationale"] for row in coverage if row["code"] == "e7"))
        self.assertIn("blank is not No", next(row["rationale"] for row in coverage if row["code"] == "g1"))
        self.assertTrue(any("privacy" in row["rationale"] for row in coverage if row["code"] == "g1"))

    def test_full_family_information_module_has_exactly_one_disposition_per_codebook_field(self):
        rows, _ = builder.build()
        ledger = builder.build_family_information_module_coverage(rows)
        self.assertEqual(len(ledger), 473)
        self.assertEqual(len({row["code"] for row in ledger}), 473)
        from collections import Counter
        counts = Counter(row["disposition"] for row in ledger)
        self.assertEqual(counts["mapped_candidate"], 431)
        self.assertEqual(counts["deferred_relative_status"], 15)
        self.assertEqual(counts["deferred_relative_attainment"], 15)
        self.assertEqual(counts["deferred_caregiver_identity"], 2)
        self.assertEqual(counts["deferred_parent_birth_year"], 6)
        self.assertEqual(counts["excluded_linkage_key"], 3)
        self.assertEqual(counts["excluded_release_metadata"], 1)

    def test_residence_timing_and_gap_migration_fields_are_complete_and_distinct(self):
        rows, _ = builder.build()
        timing = builder.build_residence_transition_coverage(rows)
        gaps = builder.build_gap_migration_reason_coverage(rows)
        self.assertEqual(len(timing), 250)
        self.assertEqual(len({row["code"] for row in timing}), 250)
        self.assertEqual(len(gaps), 169)
        self.assertEqual(len({row["code"] for row in gaps}), 169)
        self.assertTrue(all(row["concept_id"] != "life_history_residential_transition_reasons" for row in gaps))

    def test_full_residence_module_is_uniquely_dispositioned_without_location_values(self):
        from collections import Counter
        rows, _ = builder.build()
        ledger = builder.build_residence_module_coverage(rows)
        self.assertEqual(len(ledger), 935)
        self.assertEqual(len({row["code"] for row in ledger}), 935)
        counts = Counter(row["disposition"] for row in ledger)
        self.assertEqual(counts["mapped_candidate"], 827)
        self.assertEqual(counts["excluded_geographic_location_metadata"], 95)
        self.assertEqual(counts["deferred_respondent_demographic"], 6)
        self.assertEqual(counts["excluded_linkage_key"], 3)
        self.assertEqual(counts["excluded_interview_proxy_metadata"], 3)
        self.assertEqual(counts["excluded_release_metadata"], 1)

    def test_full_wealth_history_module_has_exact_dispositions_and_excludes_route_metadata(self):
        from collections import Counter
        rows, _ = builder.build()
        ledger = builder.build_wealth_history_module_coverage(rows)
        self.assertEqual(len(ledger), 440)
        self.assertEqual(len({row["code"] for row in ledger}), 440)
        counts = Counter(row["disposition"] for row in ledger)
        self.assertEqual(counts["mapped_candidate"], 432)
        self.assertEqual(counts["excluded_linkage_key"], 3)
        self.assertEqual(counts["excluded_interview_proxy_metadata"], 3)
        self.assertEqual(counts["excluded_household_route_metadata"], 1)
        self.assertEqual(counts["excluded_release_metadata"], 1)
        fs012s = next(row for row in ledger if row["code"] == "fs012s")
        self.assertEqual(fs012s["disposition"], "excluded_household_route_metadata")

    def test_full_health_history_module_has_exact_dispositions_and_none_option_is_not_exposure(self):
        from collections import Counter
        rows, _ = builder.build()
        ledger = builder.build_health_history_module_coverage(rows)
        self.assertEqual(len(ledger), 86)
        self.assertEqual(len({row["code"] for row in ledger}), 86)
        counts = Counter(row["disposition"] for row in ledger)
        self.assertEqual(counts["mapped_candidate"], 78)
        self.assertEqual(counts["excluded_none_option_metadata"], 1)
        self.assertEqual(counts["excluded_linkage_key"], 3)
        self.assertEqual(counts["excluded_interview_proxy_metadata"], 3)
        self.assertEqual(counts["excluded_release_metadata"], 1)
        none_row = next(row for row in ledger if row["code"] == "hc023s96")
        self.assertEqual(none_row["disposition"], "excluded_none_option_metadata")
        self.assertFalse(any(row["code"] == "hc023s96" for row in rows))

    def test_sample_information_has_one_mortality_candidate_and_design_metadata_dispositions(self):
        from collections import Counter
        rows, _ = builder.build()
        ledger = builder.build_sample_information_coverage(rows)
        self.assertEqual(len(ledger), 8)
        self.assertEqual(len({row["code"] for row in ledger}), 8)
        counts = Counter(row["disposition"] for row in ledger)
        self.assertEqual(counts["mapped_candidate"], 1)
        self.assertEqual(counts["excluded_linkage_key"], 3)
        self.assertEqual(counts["excluded_sample_design_metadata"], 1)
        self.assertEqual(counts["excluded_interview_timing_metadata"], 2)
        self.assertEqual(counts["excluded_release_metadata"], 1)
        self.assertFalse(any("OBS:" in " ".join(row.values()) for row in rows if row["module"] == "SAMPLEINFORMATION"))

    def test_education_history_inventory_maps_only_reviewed_fields_and_defers_remainder(self):
        from collections import Counter
        rows, _ = builder.build()
        ledger = builder.build_education_history_coverage(rows)
        self.assertEqual(len(ledger), 1105)
        self.assertEqual(len({row["code"] for row in ledger}), 1105)
        counts = Counter(row["disposition"] for row in ledger)
        self.assertEqual(counts["mapped_candidate"], 1072)
        self.assertEqual(counts["excluded_sensitive_geography"], 22)
        self.assertEqual(counts["deferred_certificate_identity_linkage"], 5)
        self.assertEqual(counts["excluded_data_quality_flag"], 1)
        self.assertEqual(counts["excluded_no_observations"], 1)
        self.assertEqual(counts["deferred_source_review"], 0)
        self.assertEqual(counts["excluded_linkage_key"], 3)
        self.assertEqual(counts["excluded_release_metadata"], 1)
        self.assertTrue(all("not yet reviewed" in row["rationale"] for row in ledger if row["disposition"] == "deferred_source_review"))


if __name__ == "__main__":
    unittest.main()
