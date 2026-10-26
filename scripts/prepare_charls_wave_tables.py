"""Build wave-specific analysis tables from original CHARLS releases.

Participant-level outputs default to LOCALAPPDATA, outside OneDrive/project
sync. Source archives are read in place and extracted only into temporary
directories. Never publish these outputs or commit/copy them to a shared path.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
from project_paths import PRIVATE_ROOT, require_private_path

WAVES = {
    "2011": ("rar", "household_and_community_questionnaire_data.rar"),
    "2013": ("zip", "CHARLS2013_Dataset.zip"),
    "2015": ("zip", "CHARLS2015r.zip"),
    "2018": ("zip", "CHARLS2018r.zip"),
    "2020": ("zip", "CHARLS2020r.zip"),
}
EXCLUDE_MODULES = {
    "child", "parent", "other_hhmember", "household_member", "sibling",
    "spousal_sibling", "household_roster", "verbal_autopsy", "exit_interview",
    "exit_module",
}
KEYS = ("ID", "householdID", "communityID")


def protected_data_path(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError(f"CHARLS inputs and outputs must stay under protected storage: {resolved}")
    return resolved


def normalize_key(series: pd.Series) -> pd.Series:
    # IDs are join keys, not numeric measurements. String normalization avoids
    # accidental int/float mismatches while preserving zero padding if present.
    out = series.astype("string").str.strip()
    out = out.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    out = out.str.replace(r"\.0+$", "", regex=True)
    return out


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_build_provenance(root: Path) -> dict[str, object]:
    """Record revision only when the working tree is clean; never infer it."""
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
            text=True, check=True,
        ).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, capture_output=True,
            text=True, check=True,
        ).stdout.strip())
        return {"git_commit": revision, "working_tree_clean": not dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"git_commit": None, "working_tree_clean": False}


def dta_members(archive: Path, kind: str):
    scratch_root = protected_data_path(PRIVATE_ROOT / "tmp")
    scratch_root.mkdir(parents=True, exist_ok=True)
    if kind == "zip":
        with zipfile.ZipFile(archive) as zf:
            bad = zf.testzip()
            if bad:
                raise RuntimeError(f"ZIP integrity failure: {archive.name}:{bad}")
            members = [n for n in zf.namelist() if n.lower().endswith(".dta")]
            with tempfile.TemporaryDirectory(prefix="charls_prep_", dir=scratch_root) as td:
                root = Path(td)
                for member in members:
                    relative = Path(member)
                    if relative.is_absolute() or ".." in relative.parts:
                        raise RuntimeError(f"Unsafe archive member path: {member}")
                    target = root / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(zf.read(member))
                    yield target
    else:
        with tempfile.TemporaryDirectory(prefix="charls_prep_2011_", dir=scratch_root) as td:
            result = subprocess.run(["tar", "-xf", str(archive), "-C", td],
                                    capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(f"Cannot extract {archive.name}: {result.stderr}")
            yield from sorted(Path(td).rglob("*.dta"))


def abbreviated(module: str) -> str:
    bits = re.findall(r"[A-Za-z0-9]+", module)
    return "".join(x[:3] for x in bits[:2]).lower() or "mod"


def unique_name(original: str, module: str, used: set[str]) -> str:
    prefix = abbreviated(module)
    base = f"{prefix}_{original}"
    if len(base) > 32:
        digest = hashlib.md5(f"{module}:{original}".encode()).hexdigest()[:5]
        base = f"{base[:26]}_{digest}"
    candidate, suffix = base, 1
    while candidate.lower() in used:
        tail = f"_{suffix}"
        candidate = base[:32-len(tail)] + tail
        suffix += 1
    used.add(candidate.lower())
    return candidate


def key_for(module: str, columns: list[str]) -> str | None:
    m = module.lower()
    if m in {"household_income", "housing_characteristics", "housing"}:
        return "householdID" if "householdID" in columns else None
    if m in {"community", "psu"}:
        return "communityID" if "communityID" in columns else None
    return next((k for k in KEYS if k in columns), None)


def split_weights(frame: pd.DataFrame, wave: str, qa: list[dict]):
    """Make respondent and household weight tables without arbitrary deduping.

    Keep official person-level sample-membership flags alongside respondent
    weights. In Wave 2 these are supplied in Weights.dta; dropping them would
    leave a prepared analytic table without the cross-section/panel distinction.
    """
    idcol, hhcol = "ID", "householdID"
    individual = [c for c in frame.columns if "weight" in c.lower() and
                  any(t in c.lower() for t in ("ind", "bio", "blood"))]
    if wave == "2013":
        required_flags = {"crosssection", "longitudinal"}
        available = {c.lower() for c in frame.columns}
        missing_flags = sorted(required_flags - available)
        if missing_flags:
            raise ValueError(
                "2013 official Weights.dta must include crosssection and "
                f"longitudinal sample flags; missing: {missing_flags}"
            )
    sample_flags = [c for c in frame.columns if (
        c.lower() in {"crosssection", "longitudinal"}
        or ("cross" in c.lower() and "section" in c.lower())
        or "longitud" in c.lower()
    )]
    individual = list(dict.fromkeys(individual + sample_flags))
    household = [c for c in frame.columns if "weight" in c.lower() and
                 any(t in c.lower() for t in ("hh", "household"))]
    parts = []
    for label, key, cols in (("Weights_person", idcol, individual),
                             ("Weights_household", hhcol, household)):
        if key not in frame.columns or not cols:
            continue
        x = frame[[key] + cols].copy()
        x[key] = normalize_key(x[key])
        x = x.loc[x[key].notna()].copy()
        variation = {c: int((x.groupby(key)[c].nunique(dropna=False) > 1).sum()) for c in cols}
        bad = sum(variation.values())
        qa.append({"wave": wave, "module": label, "merge_key": key,
                   "source_rows": len(frame), "source_unique_key_n": x[key].nunique(),
                   "source_missing_key_rows": int(frame[key].isna().sum()),
                   "base_rows_before": None, "base_missing_key_rows": None,
                   "matched_base_rows": None, "match_rate_0_to_1": None,
                   "other_id_mismatch_counts": json.dumps({"duplicate_rows": int(x[key].duplicated(keep=False).sum()),
                       "noninvariant_weight_variables": variation}, ensure_ascii=False)})
        if bad:
            continue
        parts.append((label, key, x.drop_duplicates(key, keep="first"), None))
    return parts


def merge_source(base: pd.DataFrame, incoming: pd.DataFrame, key: str,
                 module: str, wave: str, qa: list[dict], mapping: list[dict],
                 column_labels: dict[str, str], source_labels: dict[str, str]) -> pd.DataFrame:
    b = base.copy()
    inc = incoming.copy()
    b[key] = normalize_key(b[key])
    inc[key] = normalize_key(inc[key])
    b_nonnull, i_nonnull = b[key].notna(), inc[key].notna()
    b_missing, i_missing = int((~b_nonnull).sum()), int((~i_nonnull).sum())
    if (key == "ID" and b.loc[b_nonnull, key].duplicated().any()) or inc.loc[i_nonnull, key].duplicated().any():
        raise ValueError(f"Non-unique merge key {key}: wave={wave} module={module}")
    b_valid = b.loc[b_nonnull].copy()
    i_valid = inc.loc[i_nonnull].copy()
    shared = [c for c in i_valid.columns if c in b_valid.columns and c != key]
    mismatches = {}
    for col in shared:
        if key == "householdID" and col == "ID":
            # Household tables may carry the household interview respondent's
            # ID; it is not the ID of every person receiving household values.
            i_valid.drop(columns=col, inplace=True)
            continue
        left = b_valid[[key, col]].drop_duplicates(key).set_index(key)[col]
        right = i_valid.set_index(key)[col]
        common = left.index.intersection(right.index)
        both = left.loc[common].notna() & right.loc[common].notna()
        mismatches[col] = int((left.loc[common][both].astype(str) != right.loc[common][both].astype(str)).sum())
        i_valid.drop(columns=col, inplace=True)
    overlap = int(b_valid[key].isin(i_valid[key]).sum())
    used = {c.lower() for c in b.columns}
    rename = {}
    for col in i_valid.columns:
        if col != key and col in b_valid.columns:
            rename[col] = unique_name(col, module, used)
    i_valid.rename(columns=rename, inplace=True)
    for original in i_valid.columns:
        if original != key:
            column_labels[original] = source_labels.get(original, "") or ""
    for old, new in rename.items():
        column_labels[new] = source_labels.get(old, "") or ""
        mapping.append({"wave": wave, "module": module, "source_variable": old,
                        "prepared_variable": new, "reason": "name_collision"})
    validate = "one_to_one" if key == "ID" else "many_to_one"
    merged = b_valid.merge(i_valid, on=key, how="left", validate=validate, indicator="_merge_tag")
    matched = int((merged["_merge_tag"] == "both").sum())
    merged.drop(columns="_merge_tag", inplace=True)
    if b_missing:
        missing_base = b.loc[~b_nonnull].copy()
        for col in merged.columns:
            if col not in missing_base.columns:
                missing_base[col] = pd.NA
        merged = pd.concat([merged, missing_base[merged.columns]], ignore_index=True)
    qa.append({"wave": wave, "module": module, "merge_key": key,
               "source_rows": len(incoming), "source_unique_key_n": int(i_nonnull.sum()),
               "source_missing_key_rows": i_missing, "base_rows_before": len(base),
               "base_missing_key_rows": b_missing, "matched_base_rows": matched,
               "match_rate_0_to_1": round(matched / max(int(b_nonnull.sum()), 1), 6),
               "other_id_mismatch_counts": json.dumps(mismatches, ensure_ascii=False)})
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-root", type=Path,
                    help="Directory containing 原始数据+问卷2011~2020 (used for legacy/default wave paths)")
    ap.add_argument("--out-dir", type=Path,
                    default=Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) /
                    "CHARLS_ExWAS_Atlas" / "derived_wave_tables")
    ap.add_argument("--waves", default=",".join(WAVES),
                    help="Comma-separated waves to prepare, e.g. 2013 or 2013,2015")
    ap.add_argument("--wave1-all-data", type=Path,
                    help="Explicit authorized 2011 all-data ZIP or legacy RAR; stays outside the repository")
    ap.add_argument("--wave1-psu", type=Path,
                    help="Explicit authorized 2011 PSU Stata file")
    ap.add_argument("--wave1-weight", type=Path,
                    help="Explicit authorized 2011 Weight Stata file")
    ap.add_argument("--wave1-blood", type=Path,
                    help="Explicit authorized 2011 Blood Stata file")
    args = ap.parse_args()
    input_root = (protected_data_path(args.input_root) / "原始数据+问卷2011~2020"
                  if args.input_root is not None else None)
    outdir = protected_data_path(args.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    build_time = datetime.now(timezone.utc).isoformat()
    script_path = Path(__file__).resolve()
    git_provenance = git_build_provenance(script_path.parents[1])
    build_metadata = {
        "built_at_utc": build_time,
        "python_version": sys.version.split()[0],
        "pandas_version": pd.__version__,
        "pyreadstat_version": getattr(pyreadstat, "__version__", "unknown"),
        "builder_script_sha256": sha256_file(script_path),
        **git_provenance,
    }
    all_qa, all_maps, all_wave_summaries = [], [], []

    selected_waves = [w.strip() for w in args.waves.split(",") if w.strip()]
    unknown = sorted(set(selected_waves) - set(WAVES))
    if unknown:
        raise ValueError(f"Unknown waves: {unknown}")
    for wave in selected_waves:
        kind, filename = WAVES[wave]
        if wave == "2011" and args.wave1_all_data is not None:
            archive = protected_data_path(args.wave1_all_data)
            if not archive.is_file():
                raise FileNotFoundError(f"Explicit Wave 1 archive is missing: {archive}")
            suffix = archive.suffix.casefold()
            if suffix not in {".zip", ".rar"}:
                raise ValueError("Wave 1 all-data archive must be an official ZIP or legacy RAR")
            kind = "zip" if suffix == ".zip" else "rar"
        else:
            if input_root is None:
                raise ValueError(f"--input-root is required when no explicit archive is provided for wave {wave}")
            archives = sorted((input_root / wave).glob(filename))
            if len(archives) != 1:
                raise FileNotFoundError(
                    f"Expected exactly one archive named {filename} under {input_root / wave}; found {len(archives)}"
                )
            archive = archives[0]
        source_archive = {"filename": archive.name, "bytes": archive.stat().st_size,
                          "sha256": sha256_file(archive)}
        source_inputs = {"all_data_archive": source_archive}
        qa, maps, frames = [], [], []
        for file in dta_members(archive, kind):
            module = file.stem
            mkey = module.lower()
            if wave == "2011" and (
                (args.wave1_psu is not None and mkey == "psu")
                or (args.wave1_weight is not None and mkey in {"weight", "weights"})
                or (args.wave1_blood is not None and (mkey == "blood" or mkey.startswith("blood_")))
            ):
                # Explicit standalone official release files take precedence
                # over same-named modules that may also be bundled in the ZIP.
                continue
            if mkey in EXCLUDE_MODULES:
                qa.append({"wave": wave, "module": module, "merge_key": "SKIP",
                           "source_rows": None, "source_unique_key_n": None,
                           "source_missing_key_rows": None, "base_rows_before": None,
                           "base_missing_key_rows": None, "matched_base_rows": None,
                           "match_rate_0_to_1": None,
                           "other_id_mismatch_counts": "relationship/roster table excluded from respondent table"})
                continue
            frame, meta = pyreadstat.read_dta(str(file))
            if mkey in {"weights", "weight"}:
                frames.extend(split_weights(frame, wave, qa))
                continue
            key = key_for(module, frame.columns.tolist())
            if key is None:
                qa.append({"wave": wave, "module": module, "merge_key": "NOT_MERGED",
                           "source_rows": len(frame), "source_unique_key_n": None,
                           "source_missing_key_rows": None, "base_rows_before": None,
                           "base_missing_key_rows": None, "matched_base_rows": None,
                           "match_rate_0_to_1": None,
                           "other_id_mismatch_counts": "no respondent/household/community key; retained as separate source"})
                continue
            if frame[key].dropna().duplicated().any():
                qa.append({"wave": wave, "module": module, "merge_key": f"NOT_MERGED:{key}",
                           "source_rows": len(frame), "source_unique_key_n": int(frame[key].nunique()),
                           "source_missing_key_rows": int(frame[key].isna().sum()),
                           "base_rows_before": None, "base_missing_key_rows": None,
                           "matched_base_rows": None, "match_rate_0_to_1": None,
                           "other_id_mismatch_counts": "duplicate merge key; retained as separate source"})
                continue
            frames.append((module, key, frame, meta))

        if wave == "2011":
            legacy_blood = (
                input_root / wave / "Blood_20140429.dta"
                if input_root is not None and (input_root / wave / "Blood_20140429.dta").is_file()
                else None
            )
            role_inputs = (
                ("psu", args.wave1_psu, "PSU"),
                ("weight", args.wave1_weight, "Weights"),
                ("blood", args.wave1_blood or legacy_blood, "Blood_Assays"),
            )
            for role, source_path, module_name in role_inputs:
                if source_path is None:
                    continue
                source_path = protected_data_path(source_path)
                if not source_path.is_file():
                    raise FileNotFoundError(f"Explicit Wave 1 {role} file is missing: {source_path}")
                source_inputs[role] = {
                    "filename": source_path.name,
                    "bytes": source_path.stat().st_size,
                    "sha256": sha256_file(source_path),
                }
                incoming, incoming_meta = pyreadstat.read_dta(str(source_path))
                if role == "weight":
                    weight_parts = split_weights(incoming, wave, qa)
                    if not any(part[0] == "Weights_person" for part in weight_parts):
                        raise ValueError("Explicit Wave 1 Weight file did not yield a unique person-weight table")
                    frames.extend(weight_parts)
                    continue
                merge_key = key_for(module_name, incoming.columns.tolist())
                if role == "blood" and "ID" not in incoming.columns:
                    raise ValueError("Explicit Wave 1 Blood file must contain respondent ID for linkage")
                if merge_key is None:
                    raise ValueError(f"Explicit Wave 1 {role} file has no recognized merge key")
                if incoming[merge_key].dropna().duplicated().any():
                    raise ValueError(f"Explicit Wave 1 {role} file has duplicate nonmissing {merge_key} keys")
                frames.append((module_name, merge_key, incoming, incoming_meta))

        # Prefer respondent-level Demographic_Background as the analysis spine.
        spine_i = next((i for i, (m, k, _, _) in enumerate(frames)
                        if m.lower() == "demographic_background" and k == "ID"), None)
        if spine_i is None:
            raise RuntimeError(f"No unique respondent Demographic_Background spine in {wave}")
        module, key, base, base_meta = frames.pop(spine_i)
        base[key] = normalize_key(base[key])
        column_labels = {c: (lab or "") for c, lab in zip(base_meta.column_names,
                                                          base_meta.column_labels or [])}
        if base[key].dropna().duplicated().any():
            raise ValueError(f"Demographic spine is not unique in {wave}")

        # ID-level modules join to respondents; household modules join by householdID.
        id_level = [(m, k, f, me) for m, k, f, me in frames if k == "ID"]
        hh_level = [(m, k, f, me) for m, k, f, me in frames if k == "householdID"]
        community_level = [(m, k, f, me) for m, k, f, me in frames if k == "communityID"]
        separate = [(m, k, f, me) for m, k, f, me in frames if k not in {"ID", "householdID", "communityID"}]
        for m, k, f, me in id_level + hh_level:
            source_labels = {c: (lab or "") for c, lab in zip(me.column_names,
                                                               me.column_labels or [])} if me else {}
            base = merge_source(base, f, k, m, wave, qa, maps, column_labels, source_labels)
        # PSU/community information is merged only if every source key is unique;
        # otherwise it remains separate rather than creating person-row expansion.
        for m, k, f, me in community_level:
            if k == "communityID":
                source_labels = {c: (lab or "") for c, lab in zip(me.column_names,
                                                                   me.column_labels or [])} if me else {}
                base = merge_source(base, f, k, m, wave, qa, maps, column_labels, source_labels)
        for m, k, f, me in separate:
            qa.append({"wave": wave, "module": m, "merge_key": "NOT_MERGED",
                       "source_rows": len(f), "source_unique_key_n": None,
                       "source_missing_key_rows": None, "base_rows_before": None,
                       "base_missing_key_rows": None, "matched_base_rows": None,
                       "match_rate_0_to_1": None,
                       "other_id_mismatch_counts": "unrecognized key retained separately"})

        base.insert(0, "wave", int(wave))
        # Some CHARLS string-coded fields contain numeric-looking values. Pandas
        # can infer mixed Python objects after joins; normalize those back to
        # strings before writing Stata, preserving missing values.
        for col in base.columns:
            if base[col].dtype == object:
                nonmissing = base[col].notna()
                base.loc[nonmissing, col] = base.loc[nonmissing, col].map(str)
        outfile = outdir / f"CHARLS_wave{wave}_person_analytic.dta"
        var_labels = {c: label for c, label in column_labels.items() if c in base.columns}
        temp_outfile = outfile.with_name(outfile.stem + ".tmp.dta")
        pyreadstat.write_dta(base, str(temp_outfile), column_labels=var_labels,
                             version=15, file_label=f"CHARLS wave {wave} merged respondent modules")
        all_qa.extend(qa)
        all_maps.extend(maps)
        all_wave_summaries.append({"wave": wave, "rows": len(base), "columns": len(base.columns),
                                   "unique_ID": int(base["ID"].nunique(dropna=True)),
                                   "duplicate_ID": int(base["ID"].dropna().duplicated().sum()),
                                   "output": outfile.name,
                                   "source_archive": source_archive,
                                   "source_inputs": source_inputs})
        print(f"wave={wave} rows={len(base)} cols={len(base.columns)} unique_ID={base['ID'].nunique(dropna=True)}")
        pd.DataFrame(qa).to_csv(outdir / f"merge_qa_{wave}.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(maps).to_csv(outdir / f"variable_collision_map_{wave}.csv", index=False, encoding="utf-8-sig")
        _, check = pyreadstat.read_dta(str(temp_outfile), metadataonly=True)
        if check.number_rows != len(base) or check.number_columns != len(base.columns):
            raise RuntimeError(f"Read-back shape mismatch for wave {wave}")
        os.replace(temp_outfile, outfile)
        all_wave_summaries[-1]["prepared_output"] = {
            "filename": outfile.name,
            "bytes": outfile.stat().st_size,
            "sha256": sha256_file(outfile),
        }
        all_wave_summaries[-1]["build_metadata"] = build_metadata.copy()

    manifest_path = outdir / "prepared_data_manifest.json"
    prior = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"waves": []}
    known = {w["wave"]: w for w in prior.get("waves", [])}
    known.update({w["wave"]: w for w in all_wave_summaries})
    prior.update({"waves": [known[w] for w in sorted(known)],
                  "source_archives": {w: known[w].get("source_archive") for w in sorted(known)
                                      if known[w].get("source_archive")},
                  "source_inputs_by_wave": {w: known[w].get("source_inputs") for w in sorted(known)
                                            if known[w].get("source_inputs")},
                  "notes": ["person-level data; keep in private authorized storage",
                            "source archives not modified", "do not publish microdata",
                            "no row expansion by duplicate community/household keys"]})
    manifest_path.write_text(json.dumps(prior, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"out_dir={outdir}")


if __name__ == "__main__":
    main()
