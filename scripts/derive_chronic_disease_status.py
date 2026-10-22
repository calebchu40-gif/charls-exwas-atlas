#!/usr/bin/env python3
"""Derive conservative respondent-wave chronic-disease states locally.

The output contains participant IDs and must remain under LOCALAPPDATA.
Only aggregate counts are written to the project directory.
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import pandas as pd
import pyreadstat

DISEASES = {"hypertension": (1, 1), "dyslipidemia": (2, 2), "diabetes": (3, 3),
 "chronic_lung_disease": (5, 5), "heart_disease": (7, 7), "stroke": (8, 8),
 "kidney_disease": (9, 9), "arthritis": (13, 14)}
WAVES = (2011, 2013, 2015, 2018, 2020)

def getv(row: pd.Series, name: str | None):
    if not name or name not in row.index:
        return None
    x = row[name]
    if pd.isna(x) or (isinstance(x, str) and not x.strip()):
        return None
    value = pd.to_numeric(x, errors="coerce")
    return None if pd.isna(value) else int(value)

def prior_value(row: pd.Series, idx: int, panel_prior):
    if panel_prior in (0, 1):
        return int(panel_prior), "linked_prior_wave"
    for name in (f"zda007_{idx}_", f"zdisease_{idx}_"):
        v = getv(row, name)
        if v in (1, 2):
            return (1 if v == 1 else 0), f"{name}_preload"
    v = getv(row, f"zda008_{idx}_")
    if v in (1, 2):
        return (1 if v == 1 else 0), f"zda008_{idx}_preload"
    return None, "prior_unavailable"

def derive_one(wave: int, disease: str, idx: int, row: pd.Series, panel_prior):
    raw_name = f"da003_{idx}_" if wave == 2020 else f"da007_{idx}_"
    raw = getv(row, raw_name)
    conflict = 0
    source = "unresolved_missing"
    status = None
    if wave == 2011:
        if raw in (1, 2):
            status, source = (1 if raw == 1 else 0), raw_name
    elif wave in (2013, 2015):
        xtype = getv(row, "xrtype")
        prior, prior_src = prior_value(row, idx, panel_prior)
        if xtype == 1:  # NEWIW
            if raw in (1, 2):
                status, source = (1 if raw == 1 else 0), raw_name
        elif xtype == 2:  # REIW
            check = getv(row, f"da007_w2_1_{idx}_")
            interval = getv(row, f"da007_w2_2_{idx}_")
            dx_year = getv(row, f"da009_1_{idx}_")
            dx_age = getv(row, f"da009_2_{idx}_")
            reported_onset = (dx_year is not None and 1900 <= dx_year <= wave) or (dx_age is not None and 1 <= dx_age <= 120)
            if interval == 1:
                status, source = 1, f"da007_w2_2_{idx}_interval_yes"
            elif check == 2 and prior == 0 and reported_onset:
                status, source, conflict = 1, "prior_no_record_disputed_and_da009_onset_reported", 1
            elif check == 2 and interval == 2:
                # Disagrees with the recorded previous state; the official route
                # asks the interval diagnosis question to resolve the record.
                if prior is not None:
                    status, source = (1 if prior == 0 else 0), "prior_record_corrected_by_disagreement_and_no_interval_dx"
                    conflict = 1
            elif check == 1 and prior is not None:
                if prior == 1:
                    status, source = 1, "prior_diagnosis_confirmed"
                elif interval == 2:
                    status, source = 0, "prior_no_diagnosis_confirmed_no_interval_dx"
                else:
                    source = "prior_no_diagnosis_confirmed_interval_unknown"
            elif prior == 1 and check is None and interval is None:
                status, source = 1, prior_src
            elif prior == 0 and interval == 2 and check is None:
                status, source = 0, "prior_no_diagnosis_no_interval_dx"
            elif check == 2 and interval is None:
                conflict, source = 1, "prior_record_disagreed_timing_unresolved"
            if status is None and (check == 2 or interval == 2) and prior is None:
                conflict, source = 1, "returner_disagreement_prior_unavailable"
    elif wave == 2018:
        prior, prior_src = prior_value(row, idx, panel_prior)
        course = getv(row, f"da010_w2_2_{idx}_")
        if raw in (1, 2):
            status, source = (1 if raw == 1 else 0), raw_name
            if prior == 1 and raw == 2:
                conflict = 1
        elif course == 99:
            status, source, conflict = 0, f"da010_w2_2_{idx}_99_never_had", int(prior == 1)
        elif prior == 1:
            status, source = 1, prior_src
        elif prior == 0:
            source = "prior_no_diagnosis_current_unresolved"
    elif wave == 2020:
        prior, prior_src = prior_value(row, idx, panel_prior)
        course = getv(row, f"da002_{idx}_")
        if raw in (1, 2):
            status, source = (1 if raw == 1 else 0), raw_name
            if prior == 1 and raw == 2:
                conflict = 1
        elif prior == 1 and course != 99:
            status, source = 1, prior_src
        elif course == 99 and prior == 1:
            source, conflict = "course_says_absent_prior_says_diagnosed", 1
    return status, conflict, source

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, default=Path(os.environ.get("LOCALAPPDATA", ".")) / "CHARLS_ExWAS_Atlas" / "derived_chronic_disease")
    ap.add_argument("--aggregate-out", type=Path, required=True)
    args = ap.parse_args()
    if "OneDrive" in str(args.out_dir.resolve()) or "Desktop" in str(args.out_dir.resolve()):
        raise ValueError("Personal-level output must remain outside OneDrive/Desktop synchronization paths")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    prior_by_wave: dict[tuple[int, str], dict[str, int | None]] = {}
    aggregates = []
    for wave in WAVES:
        path = args.data_dir / f"CHARLS_wave{wave}_person_analytic.dta"
        _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
        columns = set(meta.column_names)
        needed = {"ID", "xrtype"}
        for disease, (idx_before, idx_2020) in DISEASES.items():
            idx = idx_2020 if wave == 2020 else idx_before
            needed.add(f"da003_{idx}_" if wave == 2020 else f"da007_{idx}_")
            if wave in (2013, 2015):
                needed.update((f"zda007_{idx}_", f"zda008_{idx}_",
                               f"da007_w2_1_{idx}_", f"da007_w2_2_{idx}_",
                               f"da009_1_{idx}_", f"da009_2_{idx}_"))
            elif wave in (2018, 2020):
                needed.update((f"zdisease_{idx}_", f"zda007_{idx}_"))
            if wave == 2018:
                needed.add(f"da010_w2_2_{idx}_")
            if wave == 2020:
                needed.add(f"da002_{idx}_")
        usecols = sorted(needed & columns)
        frame, _ = pyreadstat.read_dta(str(path), usecols=usecols)
        frame["ID"] = frame["ID"].astype("string")
        output = frame[["ID"]].copy()
        for disease, (idx_before, idx_2020) in DISEASES.items():
            idx = idx_2020 if wave == 2020 else idx_before
            prevwave = {2013: 2011, 2015: 2013, 2018: 2015, 2020: 2018}.get(wave)
            prior_map = prior_by_wave.get((prevwave, disease), {}) if prevwave else {}
            n = len(frame)
            def col(name):
                return pd.to_numeric(frame[name], errors="coerce") if name in frame else pd.Series(float("nan"), index=frame.index)
            raw_name = f"da003_{idx}_" if wave == 2020 else f"da007_{idx}_"
            raw, xtype = col(raw_name), col("xrtype")
            # Prior-wave panel status takes precedence; official preload is a
            # fallback for reinterview records that cannot be linked directly.
            prior = pd.Series(frame["ID"].astype(str).map(prior_map), index=frame.index, dtype="float64")
            for preload_name in (f"zda007_{idx}_", f"zdisease_{idx}_", f"zda008_{idx}_"):
                pre = col(preload_name)
                pre_state = pre.where(pre.isin([0, 1]), pre.map({1: 1, 2: 0}))
                prior = prior.fillna(pre_state)
            # In follow-up questionnaires these preload variables encode a
            # prior positive diagnosis; an absent preload on a reinterview is
            # the prior negative route. New interviewees remain unknown.
            reinterview_code = 2 if wave in (2013, 2015) else 1
            if wave in (2013, 2015, 2018, 2020):
                prior = prior.mask(prior.isna() & xtype.eq(reinterview_code), 0)
            status = pd.Series(float("nan"), index=frame.index)
            conflict = pd.Series(0, index=frame.index, dtype="int8")
            source = pd.Series("unresolved_missing", index=frame.index, dtype="object")
            yes, no = raw.eq(1), raw.eq(2)
            if wave == 2011:
                status.loc[yes], source.loc[yes] = 1, raw_name
                status.loc[no], source.loc[no] = 0, raw_name
            elif wave in (2013, 2015):
                check, interval = col(f"da007_w2_1_{idx}_"), col(f"da007_w2_2_{idx}_")
                dx_year, dx_age = col(f"da009_1_{idx}_"), col(f"da009_2_{idx}_")
                reported_onset = dx_year.between(1900, wave) | dx_age.between(1, 120)
                new = xtype.eq(1)
                ret = xtype.eq(2)
                status.loc[new & yes], source.loc[new & yes] = 1, raw_name
                status.loc[new & no], source.loc[new & no] = 0, raw_name
                interval_yes = ret & interval.eq(1)
                status.loc[interval_yes], source.loc[interval_yes] = 1, f"da007_w2_2_{idx}_interval_yes"
                corrected_positive = ret & check.eq(2) & prior.eq(0) & reported_onset
                status.loc[corrected_positive], source.loc[corrected_positive] = 1, "prior_no_record_disputed_and_da009_onset_reported"
                conflict.loc[corrected_positive] = 1
                corrected = ret & check.eq(2) & interval.eq(2) & prior.notna()
                status.loc[corrected] = 1 - prior.loc[corrected]
                source.loc[corrected] = "prior_record_corrected_by_disagreement_and_no_interval_dx"
                conflict.loc[corrected] = 1
                confirmed_yes = ret & check.eq(1) & prior.eq(1)
                status.loc[confirmed_yes], source.loc[confirmed_yes] = 1, "prior_diagnosis_confirmed"
                confirmed_no = ret & check.eq(1) & prior.eq(0) & interval.eq(2)
                status.loc[confirmed_no], source.loc[confirmed_no] = 0, "prior_no_diagnosis_confirmed_no_interval_dx"
                carry_yes = ret & prior.eq(1) & check.isna() & interval.isna()
                status.loc[carry_yes], source.loc[carry_yes] = 1, "linked_prior_wave"
                carry_no = ret & prior.eq(0) & interval.eq(2) & check.isna()
                status.loc[carry_no], source.loc[carry_no] = 0, "prior_no_diagnosis_no_interval_dx"
                unresolved = ret & check.eq(2) & interval.isna()
                conflict.loc[unresolved] = 1
                source.loc[unresolved] = "prior_record_disagreed_timing_unresolved"
                unavailable = ret & prior.isna() & (check.eq(2) | interval.eq(2)) & status.isna()
                conflict.loc[unavailable] = 1
                source.loc[unavailable] = "returner_disagreement_prior_unavailable"
            elif wave == 2018:
                course = col(f"da010_w2_2_{idx}_")
                status.loc[yes], source.loc[yes] = 1, raw_name
                status.loc[no], source.loc[no] = 0, raw_name
                conflict.loc[no & prior.eq(1)] = 1
                never = raw.isna() & course.eq(99)
                status.loc[never], source.loc[never] = 0, f"da010_w2_2_{idx}_99_never_had"
                conflict.loc[never & prior.eq(1)] = 1
                carry = raw.isna() & course.ne(99) & prior.eq(1)
                status.loc[carry], source.loc[carry] = 1, "linked_prior_wave_or_preload"
            else:
                course = col(f"da002_{idx}_")
                status.loc[yes], source.loc[yes] = 1, raw_name
                status.loc[no], source.loc[no] = 0, raw_name
                conflict.loc[no & prior.eq(1)] = 1
                carry = raw.isna() & course.ne(99) & prior.eq(1)
                status.loc[carry], source.loc[carry] = 1, "linked_prior_wave_or_preload"
                conflict.loc[raw.isna() & course.eq(99) & prior.eq(1)] = 1
                source.loc[raw.isna() & course.eq(99) & prior.eq(1)] = "course_says_absent_prior_says_diagnosed"
            statuses = status.tolist()
            flags = conflict.tolist()
            sources = source.tolist()
            output[f"{disease}_status"] = pd.array(statuses, dtype="Int8")
            output[f"{disease}_conflict"] = pd.array(flags, dtype="Int8")
            output[f"{disease}_source"] = sources
            vals = pd.Series(statuses, dtype="Int64")
            aggregates.append({"wave": wave, "disease": disease, "n_rows": len(frame),
                "n_yes": int((vals == 1).sum()), "n_no": int((vals == 0).sum()),
                "n_unknown": int(vals.isna().sum()), "n_conflict": int(sum(flags)),
                "status": "provisional_route_based_derived_counts"})
            prior_by_wave[(wave, disease)] = dict(zip(frame["ID"].astype(str), statuses))
        pyreadstat.write_dta(output, str(args.out_dir / f"chronic_disease_status_{wave}.dta"), version=15)
    args.aggregate_out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(aggregates).to_csv(args.aggregate_out, index=False)

if __name__ == "__main__":
    main()
