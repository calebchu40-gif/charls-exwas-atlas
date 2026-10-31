#!/usr/bin/env python3
"""Aggregate-only fasting-code diagnostic for the Wave 1 blood file.

Status: **prepared, not approved, not run on CHARLS data.**
The Wave 1 fasting field ``qc1_va003`` carries the label "Fasting" in the
released blood file, but no released official document defines its numeric
codes. Until an independent reviewer authorises an aggregate distribution check
(or CHARLS supplies the mapping), the fourteen glucose/triglyceride
coefficients stay blocked.

This script exists so that authorisation can be acted on with one command, and
so the exact aggregate output a reviewer would see is well defined in advance:

* input: the protected Wave 1 blood ``.dta`` (never copied elsewhere);
* output: counts per code and per-code means of the glucose/triglyceride
  fields — **aggregates only**, never a respondent row;
* gate: requires an explicit ``--run`` flag, a private root, and a private
  output path; without them it refuses and explains why.

The pure summariser takes plain records, so the aggregation logic is testable
without any CHARLS data and without ``polars``/``pyreadstat``.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

CODE_FIELD = "qc1_va003"
OUTCOME_FIELDS = ("newglu", "newtg")
REQUIRED_FLAG = "--run"


class DiagnosticError(ValueError):
    """The diagnostic was asked to do something it must not do."""


def _number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def summarise(records: Iterable[Mapping[str, Any]],
              code_field: str = CODE_FIELD,
              outcome_fields: tuple[str, ...] = OUTCOME_FIELDS) -> dict[str, Any]:
    """Return aggregate code counts and per-code outcome means.

    Only aggregates leave this function: counts, nulls, and means. It never
    returns a record, an identifier, or a value list.
    """
    counts: dict[str, int] = {}
    nulls = 0
    totals: dict[str, dict[str, list[float]]] = {field: {} for field in outcome_fields}
    rows = 0
    for record in records:
        rows += 1
        raw = record.get(code_field)
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            nulls += 1
            continue
        code = str(raw).strip()
        counts[code] = counts.get(code, 0) + 1
        for field in outcome_fields:
            value = _number(record.get(field))
            if value is None:
                continue
            bucket = totals[field].setdefault(code, [])
            bucket.append(value)
    summary: dict[str, Any] = {
        "rows": rows,
        "code_field": code_field,
        "code_counts": dict(sorted(counts.items())),
        "null_code_count": nulls,
        "outcomes": {},
    }
    for field in outcome_fields:
        summary["outcomes"][field] = {
            code: {"n": len(values), "mean": round(sum(values) / len(values), 6)}
            for code, values in sorted(totals[field].items())
            if values
        }
    return summary


def read_records(dta_path: Path, columns: list[str]) -> list[dict[str, Any]]:
    import pyreadstat

    frame, _ = pyreadstat.read_dta(str(dta_path), usecols=columns)
    return frame.to_dict("records")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dta", type=Path, required=True, help="protected Wave 1 blood .dta")
    parser.add_argument("--out", type=Path, required=True, help="private JSON output path")
    parser.add_argument(REQUIRED_FLAG, action="store_true",
                        help="required acknowledgement that aggregate output is authorised")
    args = parser.parse_args(argv)
    if not getattr(args, "run"):
        parser.error("--run is required: this diagnostic reads participant values and needs approval")
    if not args.dta.is_file():
        parser.error(f"input not found: {args.dta}")

    from project_paths import PRIVATE_ROOT, require_private_path

    out = require_private_path(args.out)
    if not out.is_relative_to(PRIVATE_ROOT.resolve()):
        parser.error(f"output must stay under the protected workspace {PRIVATE_ROOT}")
    source = require_private_path(args.dta)
    if not source.is_relative_to(PRIVATE_ROOT.resolve()):
        parser.error(f"input must stay under the protected workspace {PRIVATE_ROOT}")

    records = read_records(source, [CODE_FIELD, *OUTCOME_FIELDS])
    summary = summarise(records)
    summary["input_name"] = source.name
    summary["respondent_rows_exported"] = False
    summary["status"] = "empirical_only; not an official code mapping"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("rows", "code_counts", "null_code_count")},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
