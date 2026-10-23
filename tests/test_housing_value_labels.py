import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class HousingValueLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.labels = read_csv(AUDIT / "housing_value_label_review_v1.csv")
        cls.current_owner_labels = read_csv(AUDIT / "housing_current_owner_relation_labels_2018_v1.csv")
        cls.housing_mapping = read_csv(AUDIT / "housing_exposure_variable_mapping_v1.csv")
        cls.food_mapping = read_csv(AUDIT / "food_environment_crosswalk_v1.csv")
        with (ROOT / "site-prototype" / "dist" / "food_environment_v1.json").open(encoding="utf-8") as stream:
            cls.food_site = json.load(stream)
        cls.catalog = read_csv(AUDIT / "charls_atlas_candidate_fields_v0.csv")
        cls.crosswalk = read_csv(AUDIT / "ep_concept_source_crosswalk_v1.csv")
        with (ROOT / "site-prototype" / "dist" / "housing_catalog_v1.json").open(encoding="utf-8") as stream:
            cls.housing_site = json.load(stream)

    def test_structure_categories_are_wave_specific_and_omit_codebook_frequencies(self):
        labels = {(row["wave"], row["code"]): row["value_labels"] for row in self.labels}
        self.assertIn("8=Tent", labels[("2011", "i004")])
        self.assertNotIn("8=", labels[("2013", "i004")])
        self.assertIn("7=Other", labels[("2020", "i001")])
        for row in self.labels:
            self.assertNotRegex(row["value_labels"], r"\b\d{1,3},\d{3}\b|\b\d{2,}\.\d{1,2}\b|%")

    def test_2018_accessibility_keeps_do_not_need_and_2020_steps_are_continuous(self):
        lookup = {(row["wave"], row["code"]): row for row in self.labels}
        self.assertIn("3=Do not need", lookup[("2018", "i010_w4")]["value_labels"])
        self.assertIn("3=Do not need", lookup[("2020", "i009")]["value_labels"])
        self.assertNotIn(("2020", "i010"), lookup)
        catalog_row = next(row for row in self.catalog if row["Source.Wave"] == "2020" and row["Variable.Name"].lower() == "i010")
        self.assertEqual(catalog_row["Value.Labels"], "")
        self.assertIn("access-barrier measure", catalog_row["Harmonization.Status"])
        self.assertIn("not a respondent mobility test", catalog_row["Harmonization.Status"])

    def test_household_connectivity_and_air_cleaner_keep_wave_specific_codes(self):
        lookup = {(row["wave"], row["code"]): row for row in self.labels}
        for key in (("2011", "i023"), ("2013", "i023"), ("2015", "i023"), ("2018", "i023"), ("2020", "i022"),
                    ("2011", "i024"), ("2013", "i024"), ("2015", "i024"), ("2018", "i024"), ("2020", "i023"),
                    ("2015", "i027_w3"), ("2018", "i027_w3"), ("2020", "i024")):
            self.assertEqual(lookup[key]["value_labels"], "1=Yes; 2=No", key)
        self.assertEqual(lookup[("2020", "i027")]["value_labels"], "1=Flat covered; 2=Flat concrete; 3=Uneven")

    def test_residence_use_and_single_wave_housing_categories_are_labeled(self):
        lookup = {(row["wave"], row["code"]): row for row in self.labels}
        for wave in ("2011", "2013", "2015", "2018"):
            self.assertEqual(lookup[(wave, "i003")]["value_labels"], "1=Yes; 2=No")
        self.assertIn("4=Special zone", lookup[("2018", "i000_w4_2")]["value_labels"])
        self.assertIn("8=Other", lookup[("2018", "i000_w4_3")]["value_labels"])
        self.assertEqual(lookup[("2020", "i027")]["value_labels"], "1=Flat covered; 2=Flat concrete; 3=Uneven")

    def test_interviewer_observed_home_conditions_preserve_not_applicable_and_water_dk(self):
        lookup = {(row["wave"], row["code"]): row for row in self.labels}
        self.assertNotIn("6=Not applicable", lookup[("2011", "i025")]["value_labels"])
        self.assertIn("6=Not applicable", lookup[("2013", "i025")]["value_labels"])
        self.assertIn("6=Not applicable", lookup[("2013", "i026")]["value_labels"])
        self.assertIn("5=Very cold", lookup[("2011", "i026")]["value_labels"])
        self.assertEqual(lookup[("2020", "i016")]["value_labels"], "1=Yes; 2=No")
        self.assertEqual(lookup[("2020", "i029")]["value_labels"], "1=Yes; 2=No; 997=Do not know")

    def test_heating_fuels_remain_nominal_and_preserve_no_heating_codes(self):
        lookup = {(row["wave"], row["code"]): row for row in self.labels}
        for key in (("2011", "i021"), ("2013", "i021"), ("2015", "i021")):
            self.assertIn("7=Other", lookup[key]["value_labels"])
            self.assertNotIn("8=", lookup[key]["value_labels"])
        self.assertIn("8=Heating provided", lookup[("2018", "i021_w4")]["value_labels"])
        self.assertIn("8=Do not heating", lookup[("2020", "i020")]["value_labels"])
        for key in (("2011", "i020"), ("2013", "i020"), ("2015", "i020"), ("2018", "i020"), ("2020", "i019")):
            self.assertEqual(lookup[key]["value_labels"], "1=Yes; 2=No")

    def test_fuel_routes_and_source_citations_are_reviewed_across_all_five_waves(self):
        by_concept = {item["concept_id"]: item for item in self.food_site}
        for concept_id in ("heating_energy", "cooking_fuel_main"):
            fields = by_concept[concept_id]["source_fields"]
            self.assertEqual({field["wave"] for field in fields}, {"2011", "2013", "2015", "2018", "2020"})
            for field in fields:
                self.assertIn("official wave-specific questionnaire and Codebook reviewed", field["note"])
                self.assertIn("sources_official/CHARLS_", field["source_document"])
                self.assertIn("housing_fuel_source_review_2026-10-24.md", field["note"])
        heating = by_concept["heating_energy"]["caveat"]
        cooking = by_concept["cooking_fuel_main"]["caveat"]
        self.assertIn("2011–2018", heating)
        self.assertIn("XFinancialResp's house", heating)
        self.assertIn("2020 adds solar", cooking)
        self.assertIn("2018/2020 include a no-cooking response", cooking)
        self.assertIn("not measured", cooking)
        self.assertIn("XFinancialResp's house", cooking)
        self.assertIn("8=Heating Provided", next(f for f in by_concept["heating_energy"]["source_fields"] if f["wave"] == "2018")["value_labels"])
        self.assertIn("7=Solar Energy", next(f for f in by_concept["cooking_fuel_main"]["source_fields"] if f["wave"] == "2020")["value_labels"])
        app = (ROOT / "site-prototype" / "dist" / "app.js").read_text(encoding="utf-8")
        self.assertIn("field.note,field.source_document", app)

    def test_basic_sanitation_energy_and_shower_fields_keep_wave_code_shifts(self):
        lookup = {(row["wave"], row["code"]): row for row in self.labels}
        for key in (("2011", "i016"), ("2013", "i016"), ("2018", "i016"), ("2020", "i015"),
                    ("2011", "i019"), ("2013", "i019"), ("2015", "i019"), ("2018", "i019"), ("2020", "i018"),
                    ("2011", "i015"), ("2013", "i015"), ("2015", "i015"), ("2018", "i015"), ("2020", "i014")):
            self.assertEqual(lookup[key]["value_labels"], "1=Yes; 2=No", key)
        for wave in ("2011", "2013", "2015", "2018"):
            self.assertEqual(lookup[(wave, "i018")]["value_labels"], "1=Hot water provided; 2=Water heater installed by the household; 3=No")
        self.assertEqual(lookup[("2020", "i017")]["value_labels"], "1=Unified hot water supply; 2=Water heater; 3=No")
        self.assertEqual(lookup[("2020", "i016")]["value_labels"], "1=Yes; 2=No")

    def test_reviewed_labels_reach_field_catalog_concept_crosswalk_and_housing_page(self):
        key = ("2018", "i010_w4")
        field = next(row for row in self.catalog if (row["Source.Wave"], row["Variable.Name"].lower()) == (key[0], key[1]))
        self.assertEqual(field["Value.Label.Review"], "Official Codebook response categories reviewed; frequencies and percentages omitted; preserve wave-specific coding")
        self.assertEqual(field["Value.Label.Source"], "sources_official/CHARLS_2018_Codebook_extracted.txt")
        mapped = [row for row in self.crosswalk if row["Wave"] == key[0] and row["Source.Code"].lower() == key[1]]
        self.assertTrue(mapped)
        self.assertTrue(all("3=Do not need" in row["Value.Labels"] for row in mapped))
        site = [row for row in self.housing_site if row["wave"] == key[0] and row["code"].lower() == key[1]]
        self.assertTrue(site)
        self.assertTrue(all("3=Do not need" in row["value_labels"] for row in site))

    def test_2018_current_home_owner_relation_labels_do_not_infer_unobserved_categories(self):
        audit = {row["code"]: row for row in self.current_owner_labels}
        self.assertEqual(len(audit), 9)
        complete = [row for row in audit.values() if row["value_labels"]]
        partial = [row for row in audit.values() if not row["value_labels"]]
        self.assertEqual(len(complete), 1)
        self.assertEqual(len(partial), 8)
        self.assertEqual(complete[0]["value_labels"], "0=Do Not Own; 1=Own")
        self.assertTrue(all("partial response-code set" in row["value_label_status"] for row in partial))
        self.assertTrue(all("frequency" not in row["value_labels"].lower() for row in complete))
        for code, status in [(row["code"], row["value_label_status"]) for row in audit.values()]:
            field = next(row for row in self.catalog if row["Source.Wave"] == "2018" and row["Variable.Name"].lower() == code.lower())
            self.assertEqual(field["Value.Label.Review"], status)
            self.assertEqual(field["Value.Label.Source"], "sources_official/CHARLS_2018_Codebook_extracted.txt")
        site_rows = [row for row in self.housing_site if row["wave"] == "2018" and row["code"].lower().startswith("i000_w4_4_s")]
        self.assertEqual(len(site_rows), 9)
        self.assertEqual(sum(bool(row["value_labels"]) for row in site_rows), 1)

    def test_2018_current_home_owner_share_is_continuous_percent_with_explicit_limits(self):
        codes = {"i000_w4_4_1", "i000_w4_4_3", "i000_w4_4_6", "i000_w4_4_7", "i000_w4_4_8"}
        mapping = [row for row in self.housing_mapping if row["wave"] == "2018" and row["code"].lower() in codes]
        self.assertEqual({row["code"].lower() for row in mapping}, codes)
        self.assertTrue(all(row["unit"] == "% of the specific house's property rights" for row in mapping))
        self.assertTrue(all("do not sum" in row["caveat"].lower() for row in mapping))
        for code in codes:
            field = next(row for row in self.catalog if row["Source.Wave"] == "2018" and row["Variable.Name"].lower() == code)
            self.assertEqual(field["Value.Labels"], "")
            self.assertEqual(field["Concept.Unit.Candidates"], "% of the specific house's property rights")
            self.assertIn("extrema are not valid-range evidence", field["Value.Label.Review"])
            self.assertIn("do not sum across slots", field["Harmonization.Status"])
            site = next(row for row in self.housing_site if row["wave"] == "2018" and row["code"].lower() == code)
            self.assertEqual(site["unit"], "% of the specific house's property rights")

    def test_2018_current_home_area_rent_value_and_year_measures_keep_units_and_routes(self):
        expected = {
            "i000_w4_11": ("square metres", "does not own property rights", "i000_w4_12"),
            "i000_w4_12": ("square metres", "ownership route", "i000_w4_11"),
            "i000_w4_13": ("Yuan/month", "allow 0", "unfolding brackets"),
            "i000_w4_14": ("Yuan/month", "market rent", "point estimates"),
            "i000_w4_15_1": ("10,000 Yuan", "total-price", "i000_w4_15_2"),
            "i000_w4_15_2": ("1,000 Yuan/square metre", "unit-price", "i000_w4_15_1"),
            "i000_w4_16": ("calendar year", "not a duration", "special/missing values"),
            "i000_w4_17": ("10,000 Yuan", "acquire or build", "current market value"),
        }
        for code, (unit, phrase1, phrase2) in expected.items():
            field = next(row for row in self.catalog if row["Source.Wave"] == "2018" and row["Variable.Name"].lower() == code)
            self.assertEqual(field["Concept.Unit.Candidates"], unit)
            self.assertEqual(field["Value.Labels"], "")
            self.assertIn("extrema are not valid-range evidence", field["Value.Label.Review"])
            self.assertIn(phrase1.lower(), field["Harmonization.Status"].lower())
            self.assertIn(phrase2.lower(), field["Harmonization.Status"].lower())
            site = next(row for row in self.housing_site if row["wave"] == "2018" and row["code"].lower() == code)
            self.assertEqual(site["unit"], unit)
        food_areas = {row["code"] for row in self.food_mapping if row["wave"] == "2018" and row["concept_id"] == "dwelling_area"}
        self.assertTrue({"i000_w4_11", "i000_w4_12"}.issubset(food_areas))
        expected_mapping_units = {
            "i000_w4_13": "Yuan/month", "i000_w4_14": "Yuan/month",
            "i000_w4_15_1": "10,000 Yuan", "i000_w4_15_2": "1,000 Yuan/square metre",
            "i000_w4_16": "calendar year", "i000_w4_17": "10,000 Yuan",
        }
        mapping = {(row["wave"], row["code"].lower()): row for row in self.housing_mapping}
        for code, unit in expected_mapping_units.items():
            self.assertEqual(mapping[("2018", code)]["unit"], unit)

    def test_2018_household_property_values_use_measure_first_slot_second_codes(self):
        catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog}
        mapping = {(r["wave"], r["code"].lower()): r for r in self.housing_mapping}
        source_fields = {(r["wave"], r["code"].lower()): r for r in self.housing_site}
        crosswalk = {(r["Wave"], r["Source.Code"].lower()): r for r in self.crosswalk}
        for slot in range(1, 8):
            code = f"ha004_w4_1_{slot}_"
            self.assertEqual(mapping[("2018", code)]["concept_id"], "household_property_total_value_by_slot")
            self.assertEqual(mapping[("2018", code)]["unit"], "10,000 Yuan (questionnaire reporting unit)")
            row = catalog[("2018", code)]
            self.assertEqual(row["Concept.Unit.Candidates"], "10,000 Yuan")
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("preserve routing", row["Harmonization.Status"].lower())
            self.assertEqual(crosswalk[("2018", code)]["Concept.ID"], "household_property_total_value_by_slot")
            self.assertEqual(crosswalk[("2018", code)]["Unit"], "10,000 Yuan")
        for slot in range(1, 6):
            code = f"ha004_w4_2_{slot}_"
            self.assertEqual(mapping[("2018", code)]["concept_id"], "household_property_unit_value_by_slot")
            self.assertEqual(mapping[("2018", code)]["unit"], "1,000 Yuan/square metre (questionnaire reporting unit)")
            row = catalog[("2018", code)]
            self.assertEqual(row["Concept.Unit.Candidates"], "1,000 Yuan/square metre")
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("preserve routing", row["Harmonization.Status"].lower())
            self.assertEqual(crosswalk[("2018", code)]["Concept.ID"], "household_property_unit_value_by_slot")
        for slot in range(1, 8):
            code = f"ha004_w4_{slot}_"
            row = catalog[("2018", code)]
            self.assertEqual(row["epcf"], "c")
            self.assertEqual(row["Value.Labels"], "1=Total Value; 2=Unit Value")
            self.assertEqual(row["Concept.ID.Candidates"], "")
            self.assertIn("response-format selector only", row["Harmonization.Status"])
            self.assertEqual(source_fields[("2018", code)]["value_labels"], "1=Total Value; 2=Unit Value")

    def test_2018_property_value_format_selectors_are_not_exposure_concepts(self):
        selector_codes = {f"ha004_w4_{slot}_" for slot in range(1, 8)}
        rows = [
            row for row in self.crosswalk
            if row["Wave"] == "2018" and row["Source.Code"].lower() in selector_codes
        ]
        self.assertEqual(len(rows), 7)
        self.assertTrue(all(row["Role"] == "c" for row in rows))
        self.assertTrue(all(row["Catalog.Match"] == "matched" for row in rows))
        self.assertTrue(all("catalog_role_override_review_v1.csv" in row["Source.Document"] for row in rows))

    def test_2011_to_2015_housing_money_fields_keep_verified_units_and_pending_storage_limits(self):
        expected = {
            **{("2011", f"ha049_{i}_"): "Yuan" for i in range(1, 4)},
            **{("2011", f"ha047_{i}_"): "10,000 Yuan" for i in range(1, 3)},
            **{("2011", f"ha043_{i}_"): "10,000 Yuan" for i in range(1, 4)},
            ("2011", "ha023_1"): "10,000 Yuan", ("2011", "ha023_2"): "1,000 Yuan/square metre",
            ("2011", "ha022"): "10,000 Yuan", ("2011", "ha018"): "10,000 Yuan",
            **{("2013", f"ha043_{i}_"): "10,000 Yuan" for i in range(1, 5)},
            **{("2013", f"ha034_1_{i}_"): "10,000 Yuan" for i in range(1, 5)},
            **{("2013", f"ha034_2_{i}_"): "1,000 Yuan/square metre" for i in range(1, 5)},
            ("2013", "ha023_1"): "10,000 Yuan", ("2013", "ha023_2"): "1,000 Yuan/square metre",
            ("2013", "ha022"): "10,000 Yuan", ("2013", "ha018"): "10,000 Yuan",
            **{("2015", f"ha043_{i}_"): "10,000 Yuan" for i in range(1, 5)},
            **{("2015", f"ha034_1_{i}_"): "10,000 Yuan" for i in range(1, 5)},
            **{("2015", f"ha034_2_{i}_"): "1,000 Yuan/square metre" for i in range(1, 5)},
        }
        catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog}
        mapping = {(r["wave"], r["code"].lower()): r for r in self.housing_mapping}
        crosswalk = {(r["Wave"], r["Source.Code"].lower()): r for r in self.crosswalk}
        site = {(r["wave"], r["code"].lower()): r for r in self.housing_site}
        self.assertEqual(set(expected).intersection(catalog), set(expected))
        for key, unit in expected.items():
            row = catalog[key]
            self.assertEqual(row["epcf"], "e")
            self.assertEqual(row["Concept.Unit.Candidates"], unit, key)
            self.assertEqual(row["Value.Labels"], "", key)
            self.assertIn("numeric monetary amount", row["Value.Label.Review"].lower())
            self.assertIn("no discrete category labels", row["Value.Label.Review"].lower())
            self.assertIn("storage and special codes remain unverified", row["Value.Label.Review"].lower())
            self.assertIn("soft checks are interviewer prompts", row["Harmonization.Status"].lower())
            self.assertEqual(mapping[key]["unit"], unit)
            self.assertEqual(crosswalk[key]["Unit"], unit)
            self.assertEqual(site[key]["unit"], unit)

    def test_room_and_toilet_counts_are_numeric_and_wave_specific(self):
        expected = {(str(w), f"i012_{suffix}") for w in (2011, 2013, 2015, 2018) for suffix in (1, 2, 3)}
        expected |= {("2020", f"i011_{suffix}") for suffix in (1, 2, 3)}
        rows = {(row["Source.Wave"], row["Variable.Name"].lower()): row for row in self.catalog}
        self.assertTrue(expected.issubset(rows))
        for wave, code in expected:
            row = rows[(wave, code)]
            self.assertEqual(row["Concept.Unit.Candidates"], "count")
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("Codebook extrema are not valid-range evidence", row["Value.Label.Review"])
            self.assertIn("household-composition denominator", row["Harmonization.Status"])
            if wave == "2020":
                self.assertIn("Household Financial Respondent's house", row["Harmonization.Status"])
            site = next(r for r in self.housing_site if r["wave"] == wave and r["code"].lower() == code)
            self.assertEqual(site["unit"], "count")

    def test_2020_move_in_time_is_not_mapped_as_building_construction_year(self):
        mapping = {(row["wave"], row["code"]): row["concept_id"] for row in self.food_mapping}
        self.assertEqual(mapping[("2020", "i002")], "residence_move_in_time")
        self.assertEqual(mapping[("2020", "i003")], "residence_move_in_time")
        self.assertNotIn(("2020", "i002"), [(w, c) for w, c in mapping if mapping[(w, c)] == "housing_construction_year"])
        move = next(row for row in self.food_site if row["concept_id"] == "residence_move_in_time")
        self.assertIn("not when the building was constructed", move["caveat"])
        fields = {(row["wave"], row["code"]): row for row in move["source_fields"]}
        self.assertEqual(set(fields), {("2020", "i002"), ("2020", "i003")})
        self.assertIn("1=0-5 years", fields[("2020", "i003")]["value_labels"])

    def test_housing_area_and_construction_year_units_are_questionnaire_backed(self):
        expected = {
            ("2011", "i001"): "square metres", ("2013", "i001"): "square metres",
            ("2020", "i028"): "square metres", ("2011", "i005"): "calendar year",
            ("2013", "i005"): "calendar year", ("2015", "i005"): "calendar year",
            ("2018", "i005"): "calendar year", ("2020", "i002"): "calendar year",
        }
        catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog}
        for key, unit in expected.items():
            row = catalog[key]
            self.assertEqual(row["Concept.Unit.Candidates"], unit)
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("authorized release", row["Harmonization.Status"])
        self.assertIn("not the building construction year", catalog[("2020", "i002")]["Harmonization.Status"])

    def test_weekly_food_spending_units_keep_household_scope_and_wave_exclusions(self):
        expected = {
            ("2011", "ge006"), ("2013", "ge006"), ("2015", "ge006"),
            ("2018", "ge006_w4"), ("2020", "gf006"),
            ("2011", "ge007"), ("2013", "ge007"), ("2015", "ge007"),
            ("2018", "ge007_w4"), ("2020", "gf009"),
        }
        catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog}
        for wave, code in expected:
            row = catalog[(wave, code)]
            self.assertEqual(row["Concept.Unit.Candidates"], "Yuan/week")
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("not individual dietary intake", row["Harmonization.Status"])
            self.assertIn("cross-wave equivalence", row["Harmonization.Status"])
        self.assertIn("includes purchased and own-produced food", catalog[("2011", "ge006")]["Harmonization.Status"])
        site_rows = {
            (field["wave"], field["code"].lower()): field
            for concept in self.food_site
            if concept["concept_id"] in {"household_food_expenditure", "household_eating_out"}
            for field in concept["source_fields"]
        }
        for key in expected:
            self.assertIn("Official", site_rows[key]["note"])
            self.assertNotIn("questionnaire review pending", site_rows[key]["note"])
            self.assertIn("household_food_expenditure_measure_review_2026-10-23.md", site_rows[key]["note"])
            self.assertIn("sources_official/", site_rows[key]["source_document"])

    def test_weekly_food_spending_review_status_matches_domain_crosswalk(self):
        expected = {
            ("2011", "ge006"), ("2013", "ge006"), ("2015", "ge006"),
            ("2018", "ge006_w4"), ("2020", "gf006"),
            ("2011", "ge007"), ("2013", "ge007"), ("2015", "ge007"),
            ("2018", "ge007_w4"), ("2020", "gf009"),
        }
        rows = {
            (row["wave"], row["code"].lower()): row
            for row in self.food_mapping
            if row["concept_id"] in {"household_food_expenditure", "household_eating_out"}
        }
        self.assertEqual(set(rows), expected)
        for key, row in rows.items():
            self.assertIn("official", row["mapping_status"])
            self.assertIn("cross-wave construct comparability not approved", row["mapping_status"])
            self.assertIn("not individual dietary intake", row["caveat"])
            self.assertIn("own-production treatment and exclusions vary by wave", row["caveat"].lower())
            self.assertNotRegex(row["code_value_labels"], r"\bFreq\b|\b%")

    def test_household_food_roles_and_shared_meal_count_keep_distinct_measurement_levels(self):
        catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog}
        mapping = {(f["wave"], f["code"].lower()): f for concept in self.food_site for f in concept["source_fields"]}
        for wave, yes, who, count in [
            ("2011", "ge001", "ge002", "ge004"),
            ("2013", "ge001", "ge002", "ge004"),
            ("2015", "ge001", "ge002", "ge004"),
            ("2018", "ge001", "ge002", "ge004"),
            ("2020", "gf002", "gf003", "gf004"),
        ]:
            self.assertEqual(catalog[(wave, yes)]["Value.Labels"], "1=Yes; 2=No")
            self.assertEqual(catalog[(wave, who)]["Value.Labels"], "")
            self.assertIn("roster", catalog[(wave, who)]["Value.Label.Review"])
            self.assertEqual(catalog[(wave, count)]["Unit"], "persons")
            self.assertIn("excluding guests", catalog[(wave, count)]["Harmonization.Status"])
            self.assertEqual(mapping[(wave, count)]["unit"], "persons")

    def test_building_floor_and_entrance_access_measures_are_wave_specific(self):
        catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog}
        fields = {(f["wave"], f["code"].lower()): f for concept in self.food_site for f in concept["source_fields"]}
        for wave, code, unit, phrase in [
            ("2011", "i008", "storeys", "ordinal/numeric floor position"),
            ("2013", "i008", "storeys", "ordinal/numeric floor position"),
            ("2015", "i008", "storeys", "ordinal/numeric floor position"),
            ("2018", "i008", "storeys", "ordinal/numeric floor position"),
            ("2020", "i006_1", "storeys", "above-ground storey"),
            ("2020", "i006_2", "storeys", "underground storey"),
            ("2020", "i010", "steps", "access-barrier measure"),
        ]:
            row = catalog[(wave, code)]
            self.assertEqual(row["Unit"], unit)
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn(phrase, row["Harmonization.Status"])
            self.assertEqual(fields[(wave, code)]["unit"], unit)
        selector = catalog[("2020", "i006")]
        self.assertEqual(selector["Value.Labels"], "1=On the ground; 2=Underground")
        self.assertEqual(selector["Unit"], "")

    def test_toilet_access_labels_preserve_split_and_single_item_waves(self):
        catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog}
        fields = {(f["wave"], f["code"].lower()): f for concept in self.food_site for f in concept["source_fields"]}
        for wave, code, labels in [
            ("2011", "i014s1", "1=Toilet without a seat"), ("2011", "i014s2", "2=Toilet with a seat"),
            ("2013", "i014s1", "1=Toilet without a seat"), ("2013", "i014s2", "2=Toilet with a seat"),
            ("2015", "i014s1", "1=Toilet without a seat"), ("2015", "i014s2", "2=Toilet with a seat"),
            ("2018", "i014", "1=Toilet without a seat; 2=Toilet with a seat"),
            ("2020", "i013", "1=Toilet without a seat; 2=Toilet with a seat"),
        ]:
            self.assertEqual(catalog[(wave, code)]["Value.Labels"], labels)
            if wave in ("2011", "2013", "2015"):
                self.assertIn("Do not infer", catalog[(wave, code)]["Harmonization.Status"])
            self.assertEqual(fields[(wave, code)]["value_labels"], labels)
        for wave, code in [("2011", "i013"), ("2013", "i013"), ("2015", "i013"), ("2018", "i013"), ("2020", "i012")]:
            self.assertEqual(catalog[(wave, code)]["Unit"], "meters")
            self.assertEqual(catalog[(wave, code)]["Value.Labels"], "")

    def test_individual_meal_frequency_is_two_wave_ordered_behavior_measure(self):
        catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog}
        for wave in ("2011", "2013"):
            row = catalog[(wave, "da058")]
            self.assertEqual(row["Value.Labels"], "1=More than 4 meals per day; 2=4 meals per day; 3=3 meals per day; 4=2 meals per day; 5=1 meal per day; 6=<1 meal per day")
            self.assertIn("ordinal behavior measure", row["Harmonization.Status"])
            self.assertIn("not dietary quality", row["Harmonization.Status"])

    def test_kitchen_and_balcony_counts_are_household_numeric_measures(self):
        catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog}
        for wave in ("2011", "2013", "2015", "2018"):
            for code in ("i012_4", "i012_5"):
                row = catalog[(wave, code)]
                self.assertEqual(row["Unit"], "count")
                self.assertEqual(row["Value.Labels"], "")
                self.assertIn("household-level built-environment context", row["Harmonization.Status"].lower())

    def test_homestead_area_units_and_zero_applicability_are_preserved(self):
        catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog}
        for wave in ("2011", "2013", "2015", "2018"):
            row = catalog[(wave, "i002")]
            self.assertEqual(row["Unit"], "m²")
            self.assertIn("rural collective", row["Harmonization.Status"])
            self.assertIn("potentially structural/nonapplicable", row["Harmonization.Status"])
            self.assertIn("not validated analytic bounds", row["Harmonization.Status"])

    def test_2018_property_count_and_rent_status_respect_route_and_slots(self):
        catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog}
        count = catalog[("2018", "ha000_w4_0")]
        self.assertEqual(count["Unit"], "properties")
        self.assertIn("new-household route only", count["Harmonization.Status"])
        for i in range(1, 8):
            row = catalog[("2018", f"ha005_w4_{i}_")]
            self.assertEqual(row["Value.Labels"], "1=Yes; 2=No; 999=Refuse to answer")
            self.assertIn("Keep each property slot separate", row["Harmonization.Status"])

    def test_2018_actual_and_market_rents_keep_units_routes_and_slots(self):
        catalog = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in self.catalog}
        for code, phrase in [(f"ha006_w4_{i}_", "routed after HA005=Yes") for i in (1,2,3,4,5,7)]:
            row = catalog[("2018", code)]
            self.assertEqual(row["Unit"], "Yuan/month")
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn(phrase, row["Harmonization.Status"])
        for i in range(1,8):
            row = catalog[("2018", f"ha007_w4_{i}_")]
            self.assertEqual(row["Unit"], "Yuan/month")
            self.assertIn("separate estimated amount", row["Harmonization.Status"])
        self.assertIn("excludes banquets/weddings", catalog[("2020", "gf006")]["Harmonization.Status"])
        self.assertIn("excludes banquets/weddings", catalog[("2018", "ge007_w4")]["Harmonization.Status"])


if __name__ == "__main__":
    unittest.main()
