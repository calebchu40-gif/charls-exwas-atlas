import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def test_mortality_mapping_is_limited_to_reviewed_exit_fields_and_roles():
    rows = read_csv(ROOT / "audit/mortality_endpoint_crosswalk_v1.csv")
    assert len(rows) == 11
    assert len({(row["wave"], row["code"]) for row in rows}) == len(rows)
    assert {row["wave"] for row in rows} == {"2013", "2020"}
    assert {row["code"] for row in rows if row["wave"] == "2013"} == {
        "exb001_1", "exb001_2", "exb002", "exb009"
    }
    assert {row["code"] for row in rows if row["wave"] == "2020"} == {
        "exb001_1", "exb001_2", "exb001_3", "exb002", "exb007", "exb008", "exb008_1"
    }
    assert all("proxy" in row["caveat"].lower() or "decedent" in row["caveat"].lower() for row in rows)
    assert all("frequency" not in row["value_semantics"].lower() for row in rows)


def test_mortality_mapping_source_wording_and_route_caveats_are_documented():
    rows = read_csv(ROOT / "audit/mortality_endpoint_crosswalk_v1.csv")
    for row in rows:
        assert (ROOT / row["source_document"]).is_file()
    questionnaire = (ROOT / "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt").read_text(
        encoding="utf-8", errors="replace"
    )
    assert "EXB001 What was the date" in questionnaire
    assert "EXB002 Is the date of death based on the solar or the lunar calendar?" in questionnaire
    assert "EXB008 About how long was it between the start of the final illness" in questionnaire
    duration = next(row for row in rows if row["code"] == "exb008_1")
    assert "only when exb008" in duration["value_semantics"]
    assert "not treat routed missing values as zero" in duration["caveat"]


def test_aggregated_mortality_calendar_is_metadata_and_endpoints_are_candidates():
    rows = read_csv(ROOT / "audit/ep_concept_source_crosswalk_v1.csv")
    mortality = [row for row in rows if row["Concept.ID"].startswith("mortality_")]
    assert len(mortality) == 11
    assert {row["Role"] for row in mortality if row["Concept.ID"] == "mortality_date_calendar"} == {"c"}
    assert {row["Role"] for row in mortality if row["Concept.ID"] != "mortality_date_calendar"} == {"p"}
    assert all("candidate" in row["Mapping.Status"].lower() for row in mortality)
    assert all("all-cohort" in row["Caveat"].lower() or "decedent" in row["Caveat"].lower() for row in mortality)


def test_mortality_sources_are_present_in_the_searchable_candidate_catalog():
    rows = read_csv(ROOT / "audit/charls_atlas_candidate_fields_v0.csv")
    mortality = [row for row in rows if row.get("Concept.ID.Candidates", "").startswith("mortality_")]
    assert len(mortality) == 11
    mapped = {(row["Source.Wave"], row["Variable.Name"].lower(), row["epcf"]) for row in mortality}
    expected = {
        (row["wave"], row["code"], row["role"])
        for row in read_csv(ROOT / "audit/mortality_endpoint_crosswalk_v1.csv")
    }
    assert mapped == expected
    assert all("candidate" in row["Candidate.Status"].lower() for row in mortality)
    assert all(row["Value.Label.Review"].strip().lower() != "not yet reviewed" for row in mortality)
    assert all("frequency" not in row["Value.Labels"].lower() for row in mortality)
