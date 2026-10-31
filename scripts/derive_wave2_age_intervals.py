"""Derive protected, provisional Wave 2 age intervals from source-resolved inputs.

Age intervals account for the unknown interview day and for unresolved birth
calendar routes. The official CHARLS Mata lookup has source-only parity with
the pinned python-lunardate implementation; no respondent-level output leaves
the protected workspace. This script does not approve an age estimand or fit
associations.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from calendar import monthrange
from collections import Counter
from datetime import date
from pathlib import Path

import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent
if (Path.cwd() / "scripts").is_dir():
    sys.path.insert(0, str(Path.cwd() / "scripts"))
else:
    sys.path.insert(0, str(HERE))
from project_paths import PRIVATE_ROOT, WAVE_DATA_DIR, QA_OUTPUT_DIR, require_private_path
from verify_official_lunar_table_parity import validate as validate_official_lunar_mapping


LUNARDATE_SHA256 = "3b2eb1b90ec8107a7bd8a852a4efacd54ca4d3f5ce862145cfd5500e52ffed52"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def private(path: Path) -> Path:
    p = require_private_path(path)
    if not p.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Wave 2 age inputs and outputs must remain under protected storage")
    return p


def n(value):
    x = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(x) or float(x) != int(float(x)):
        return None
    return int(x)


def age_on(birth: date, interview: date) -> int:
    return interview.year - birth.year - ((interview.month, interview.day) < (birth.month, birth.day))


def load_converter(path: Path):
    if sha256(path) != LUNARDATE_SHA256:
        raise ValueError("Pinned lunar converter SHA-256 mismatch")
    spec = importlib.util.spec_from_file_location("charls_pinned_lunardate_014", path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load pinned lunar conversion source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--age-input", type=Path,
                    default=WAVE_DATA_DIR / "CHARLS_wave2013_age_inputs_source_bound.dta")
    ap.add_argument("--input-qa", type=Path,
                    default=QA_OUTPUT_DIR / "wave2_age_input_source_reconciliation_private.json")
    ap.add_argument("--output", type=Path,
                    default=WAVE_DATA_DIR / "CHARLS_wave2013_age_interval_candidate.dta")
    ap.add_argument("--qa-output", type=Path,
                    default=QA_OUTPUT_DIR / "wave2_age_interval_candidate_private.json")
    ap.add_argument("--converter", type=Path,
                    default=PRIVATE_ROOT / "references/lunardate_0.1.4/lunardate-0.1.4/lunardate.py")
    ap.add_argument("--official-mmat", type=Path,
                    default=PRIVATE_ROOT / "references/charls_official_lunar2solar.mmat")
    args = ap.parse_args()
    for field in ("age_input", "input_qa", "output", "qa_output", "converter", "official_mmat"):
        setattr(args, field, private(getattr(args, field)))
    input_qa = json.loads(args.input_qa.read_text(encoding="utf-8"))
    if input_qa.get("status") != "source_reconciliation_complete_age_not_calculated":
        raise ValueError("Wave 2 source reconciliation is not complete")
    if input_qa.get("output_sha256") != sha256(args.age_input):
        raise ValueError("Source-resolved Wave 2 age inputs do not match their protected QA hash")
    parity = validate_official_lunar_mapping(args.official_mmat, args.converter)
    lunar = load_converter(args.converter)
    frame, _ = pyreadstat.read_dta(str(args.age_input), usecols=[
        "ID", "dob_route_status", "dob_year_source", "dob_month_source", "dob_day_source",
        "dob_calendar_source", "age_fallback_ba004_w2", "interview_year_source", "interview_month_source",
    ])
    if frame.ID.isna().any() or frame.ID.astype("string").str.strip().eq("").any() or frame.ID.duplicated().any():
        raise ValueError("Protected Wave 2 age-input IDs must be present and unique")
    rows, routes, domains, invalid = [], Counter(), Counter(), Counter()
    for row in frame.itertuples(index=False, name=None):
        (rid, route_src, raw_y, raw_m, raw_d, raw_cal, raw_age, raw_iy, raw_im) = row
        y, m, d, cal, fallback, iy, im = map(n, (raw_y, raw_m, raw_d, raw_cal, raw_age, raw_iy, raw_im))
        lo = hi = None
        route = "unresolved_source_route"
        leap_ambiguous = False
        if iy is None or im is None or not 1 <= im <= 12:
            route = "missing_or_invalid_interview_month"
        elif y is not None and 1900 <= y <= iy and cal in (1, 2):
            complete = m is not None and d is not None and 1 <= m <= 12 and 1 <= d <= 31
            if cal == 1 and complete:
                try:
                    birth = date(y, m, d)
                    first, last = date(iy, im, 1), date(iy, im, monthrange(iy, im)[1])
                    lo, hi = sorted((age_on(birth, first), age_on(birth, last)))
                    route = "solar_full_date_interview_day_unknown"
                except ValueError:
                    route = "invalid_solar_date"
                    invalid[route] += 1
            elif cal == 2 and complete:
                key = y * 10000 + m * 100 + d
                try:
                    if not 19000101 <= key <= 20401128:
                        raise ValueError("outside CHARLS converter domain")
                    leap_month = lunar.yearInfos[y - 1900] % 16
                    leap_ambiguous = leap_month == m
                    if leap_ambiguous:
                        try:
                            lunar.LunarDate(y, m, d, False).toSolarDate()
                        except ValueError:
                            lunar.LunarDate(y, m, d, True).toSolarDate()
                        lo, hi = max(0, iy - y - 2), iy - y
                        route = "lunar_leap_month_ambiguous_interval"
                    else:
                        birth = lunar.LunarDate(y, m, d, False).toSolarDate()
                        first, last = date(iy, im, 1), date(iy, im, monthrange(iy, im)[1])
                        lo, hi = sorted((age_on(birth, first), age_on(birth, last)))
                        route = "lunar_official_default_interview_day_unknown"
                except (ValueError, IndexError, OverflowError):
                    route = "invalid_or_out_of_domain_lunar_date"
                    invalid[route] += 1
            elif cal == 1 and m is not None and 1 <= m <= 12:
                base = iy - y
                if m < im:
                    lo = hi = base
                elif m > im:
                    lo = hi = base - 1
                else:
                    lo, hi = max(0, base - 1), base
                route = "solar_month_known_day_incomplete_interval"
            else:
                lo, hi = max(0, iy - y - 2), iy - y
                route = "partial_date_interval"
        elif y is not None and 1900 <= y <= (iy if iy is not None else 0):
            lo, hi = max(0, iy - y - 2), iy - y
            route = "calendar_unresolved_year_interval"
        elif fallback is not None and 1 <= fallback <= 120 and y is None and m is None and d is None and cal is None:
            lo = hi = fallback
            route = "conditional_self_reported_age_all_date_components_missing"
        else:
            route = "no_supported_age_input"
        if lo is not None and (lo < 0 or hi > 120 or lo > hi):
            lo = hi = None
            route = "age_interval_out_of_range"
            invalid[route] += 1
        domain = "age_unresolved" if lo is None else (
            "45plus_definite" if lo >= 45 else "45plus_ambiguous" if hi >= 45 else "below45_definite"
        )
        routes[route] += 1
        domains[domain] += 1
        rows.append({"ID": str(rid).strip(), "age_at_interview_lower": lo,
                     "age_at_interview_upper": hi, "age_route": route,
                     "leap_month_ambiguity": int(leap_ambiguous),
                     "age45_domain_status_candidate": domain,
                     "dob_source_route": str(route_src)})
    result = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pyreadstat.write_dta(result, str(args.output), version=14,
                         file_label="Protected Wave 2 provisional age intervals; not analysis approved")
    os.chmod(args.output, 0o600)
    report = {
        "scope": "protected provisional Wave 2 age-interval candidate; no association models",
        "source_age_input_sha256": sha256(args.age_input),
        "official_lunar_mapping_parity": parity,
        "person_level_candidate_sha256": sha256(args.output),
        "row_count": int(len(result)), "route_counts_private": dict(sorted(routes.items())),
        "age45_domain_counts_private": dict(sorted(domains.items())),
        "invalid_counts_private": dict(sorted(invalid.items())),
        "interview_day_available": False, "separate_leap_month_response_available": False,
        "age_used_to_filter_rows": False, "age_method_reviewed": False,
        "variance_method_frozen": False, "association_models_fitted": False,
    }
    args.qa_output.parent.mkdir(parents=True, exist_ok=True)
    args.qa_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(args.qa_output, 0o600)
    print("Wave 2 age intervals derived to protected candidate table; exact QA remains private; no model fitted.")


if __name__ == "__main__":
    main()
