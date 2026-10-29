"""Reconcile Wave 1 respondent, weight, blood, and PSU keys in private storage.

Only identifier/PSU-key columns and the official individual/blood weight fields
are read. The report contains aggregate counts and gate status only and must
remain under the protected CHARLS root. No questionnaire, exposure, or outcome
values are read; no associations are estimated and no identifiers are written.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path
from require_verified_wave1_frame import require_verified_wave1_frame


DEFAULT_DATA = PRIVATE_ROOT / "derived_wave_tables" / "CHARLS_wave2011_person_analytic.dta"
DEFAULT_INTAKE = PRIVATE_ROOT / "incoming_2011_official"
DEFAULT_OUTPUT = PRIVATE_ROOT / "qa_outputs" / "wave1_official_frame_reconciliation.json"
OFFICIAL_DENOMINATORS = {
    "baseline_interviews_and_blood_target": {
        "n": 17708,
        "source": "CHARLS National Baseline Users' Guide and Blood Data Users' Guide",
        "urls": [
            "https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/CHARLS_nationalbaseline_users_guide.pdf",
            "https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf",
        ],
    },
    "codebook_person_id_observations": {
        "n": 17705,
        "source": "CHARLS 2011 Codebook, Demographic Background: ID",
        "url": "https://charls.pku.edu.cn/en/Data/a2011_CHARLS_Wave1__Baseline_.htm",
    },
    "codebook_individual_weight_observations": {
        "n": 17708,
        "source": "CHARLS 2011 Codebook, Weight: individual weight fields",
        "url": "https://charls.pku.edu.cn/en/Data/a2011_CHARLS_Wave1__Baseline_.htm",
    },
}


def private_path(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Wave 1 frame reconciliation inputs/outputs must stay under protected storage")
    return resolved


def normalized_ids(path: Path, columns: list[str] | None = None) -> tuple[pd.DataFrame, pd.Index, int]:
    usecols = list(dict.fromkeys(["ID", *(columns or [])]))
    frame, _ = pyreadstat.read_dta(str(private_path(path)), usecols=usecols)
    values = frame["ID"].astype("string").str.strip()
    values = values.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    values = values.str.replace(r"\.0+$", "", regex=True)
    frame["_normalized_id"] = values
    valid = values.dropna()
    return frame, pd.Index(valid.unique()), int(values.isna().sum())


def run(data: Path, intake: Path) -> dict[str, object]:
    data = private_path(data)
    intake = private_path(intake)
    if not data.is_file() or not intake.is_dir():
        raise FileNotFoundError("Protected Wave 1 prepared frame or official intake is missing")

    weight_path = private_path(intake / "weight.dta")
    blood_path = private_path(intake / "Blood_20140429.dta")
    psu_path = private_path(intake / "PSU.dta")
    person_frame, ids, frame_missing = normalized_ids(data, ["communityID"])
    weight_frame, weight_ids, weight_missing = normalized_ids(weight_path, ["ind_weight_ad2"])
    blood_frame, blood_ids, blood_missing = normalized_ids(blood_path, ["bloodweight"])
    frame_rows = len(person_frame)
    weight_rows = len(weight_frame)
    blood_rows = len(blood_frame)

    weight_value = pd.to_numeric(weight_frame["ind_weight_ad2"], errors="coerce")
    weight_observed_ids = pd.Index(weight_frame.loc[weight_value.notna(), "_normalized_id"].dropna().unique())
    weight_valid_ids = pd.Index(weight_frame.loc[weight_value.gt(0), "_normalized_id"].dropna().unique())
    blood_weight_value = pd.to_numeric(blood_frame["bloodweight"], errors="coerce")
    blood_weight_valid_ids = pd.Index(blood_frame.loc[blood_weight_value.gt(0), "_normalized_id"].dropna().unique())

    psu_frame, _ = pyreadstat.read_dta(str(psu_path), usecols=["communityID"])
    psu_keys = psu_frame["communityID"].astype("string").str.strip()
    psu_keys = psu_keys.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    respondent = person_frame
    respondent_keys = respondent["communityID"].astype("string").str.strip()
    respondent_keys = respondent_keys.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    unique_psu = pd.Index(psu_keys.dropna().unique())
    unique_respondent_psu = pd.Index(respondent_keys.dropna().unique())

    source = require_verified_wave1_frame(data_path=data)
    comparisons = {
        "prepared_person_frame": {"rows": frame_rows, "unique_ids": len(ids), "missing_id_rows": frame_missing},
        "official_weight_file": {
            "rows": weight_rows,
            "unique_ids": len(weight_ids),
            "missing_id_rows": weight_missing,
            "ids_matching_person_frame": len(ids.intersection(weight_ids)),
            "weight_ids_not_in_person_frame": len(weight_ids.difference(ids)),
            "ind_weight_ad2_nonmissing_ids": len(weight_observed_ids),
            "nonmissing_ind_weight_ad2_ids_matching_person_frame": len(ids.intersection(weight_observed_ids)),
            "nonmissing_ind_weight_ad2_ids_outside_person_frame": len(weight_observed_ids.difference(ids)),
            "ind_weight_ad2_positive_ids": len(weight_valid_ids),
            "positive_ind_weight_ad2_ids_matching_person_frame": len(ids.intersection(weight_valid_ids)),
            "positive_ind_weight_ad2_ids_outside_person_frame": len(weight_valid_ids.difference(ids)),
        },
        "official_blood_file": {
            "rows": blood_rows,
            "unique_ids": len(blood_ids),
            "missing_id_rows": blood_missing,
            "ids_matching_person_frame": len(ids.intersection(blood_ids)),
            "blood_ids_not_in_person_frame": len(blood_ids.difference(ids)),
            "bloodweight_positive_ids": len(blood_weight_valid_ids),
            "positive_bloodweight_ids_matching_person_frame": len(ids.intersection(blood_weight_valid_ids)),
        },
        "official_psu_file": {
            "rows": len(psu_frame),
            "unique_community_keys": len(unique_psu),
            "missing_community_rows": int(psu_keys.isna().sum()),
            "respondent_community_keys_matching_psu": len(unique_respondent_psu.intersection(unique_psu)),
            "respondent_community_keys_unmatched": len(unique_respondent_psu.difference(unique_psu)),
            "final_sub_psu_and_strata_resolved": False,
        },
    }
    official_n = OFFICIAL_DENOMINATORS["baseline_interviews_and_blood_target"]["n"]
    blood_target_weight_count_matches = len(weight_observed_ids) == official_n
    positive_weight_ids_outside_frame = len(weight_valid_ids.difference(ids))
    blood_ids_all_match = len(blood_ids.difference(ids)) == 0
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "audit_type": "protected identifier-key and denominator reconciliation",
        "non_identifier_respondent_values_read": False,
        "individual_identifiers_processed_in_memory": True,
        "association_models_estimated": False,
        "individual_identifiers_written": False,
        "source_identity_status": source["source_identity_status"],
        "source_manifest_id": source["source_manifest_id"],
        "prepared_table_sha256": source["prepared_output_sha256"],
        "official_denominator_references": OFFICIAL_DENOMINATORS,
        "weight_semantics_from_official_documents": {
            "ind_weight_ad2": "Individual weight with household and individual non-response adjustment (CHARLS 2011 Codebook).",
            "bloodweight": "Blood-specific weight adjusting household and individual survey non-response and blood non-participation (CHARLS Blood Data Users' Guide).",
        },
        "prepared_frame_minus_published_blood_target": frame_rows - official_n,
        "ind_weight_ad2_nonmissing_ids_match_published_target_count": blood_target_weight_count_matches,
        "positive_bloodweight_ids_all_match_person_frame": blood_ids_all_match,
        "component_key_comparisons": comparisons,
        "gates": {
            "source_identity": "passed",
            "respondent_frame_unique_id": "passed" if frame_missing == 0 and len(ids) == frame_rows else "blocked",
            "weight_and_blood_key_reconciliation": "partially_reconciled",
            "official_target_denominator": "partially_reconciled" if blood_target_weight_count_matches else "unresolved",
            "positive_weight_id_person_spine_linkage": "unresolved" if positive_weight_ids_outside_frame else "passed",
            "blood_file_id_person_spine_linkage": "passed" if blood_ids_all_match else "unresolved",
            "final_psu_strata_and_variance": "unresolved",
            "formal_model_gate": "not_passed",
        },
        "limitations": [
            "Published counts refer to different file/field targets and are not interchangeable.",
            "A key match does not establish module eligibility, response adjustment validity, age-domain validity, or causal interpretation.",
            "The PSU key check does not recover split-community final PSU assignment or county-stage strata.",
            "This report is aggregate-only private QA and is not a result for public release.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--intake", type=Path, default=DEFAULT_INTAKE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = run(args.data, args.intake)
    output = private_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wave 1 official frame reconciliation: complete; formal model gate remains not passed")
    print(f"Aggregate-only report saved under protected storage: {output}")


if __name__ == "__main__":
    main()
