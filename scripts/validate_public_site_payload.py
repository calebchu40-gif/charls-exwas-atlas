"""Fail closed when the GitHub Pages payload contains non-site files."""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from pathlib import Path

from adjust_exwas_pvalues import adjust_pvalues


ALLOWED_SUFFIXES = {".css", ".gif", ".html", ".ico", ".jpeg", ".jpg", ".js", ".json", ".png", ".svg", ".webp", ".woff", ".woff2"}
ALLOWED_DOTFILES = {".nojekyll"}
RESULT_TOP_FIELDS = {"schema_version", "release_status", "generated_at", "families"}
RESULT_FAMILY_FIELDS = {"family_id", "family_size", "rows"}
PUBLIC_VARIANCE_LABELS = {
    "Survey design verified",
    "Approximate variance; official stratum unavailable",
    "Design not fit-ready",
}
RESULT_ROW_FIELDS = {
    "analysis_id", "data_release", "wave", "exposure_concept_id", "exposure_variable",
    "phenotype_concept_id", "phenotype_variable", "target_population", "model_id",
    "estimate_type", "contrast", "estimate", "standard_error", "ci_lower", "ci_upper",
    "p_value", "q_value_by", "p_bonferroni", "n_model", "fit_status",
    "variance_design", "comparability_grade", "disclosure_status",
}


def validate_association_payload(payload: object) -> list[str]:
    """Validate the strict, disclosure-reviewed browser result contract."""
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["Association result payload must be a JSON object"]
    if set(payload) != RESULT_TOP_FIELDS:
        errors.append("Association result payload has missing or non-allowlisted top-level fields")
    if payload.get("schema_version") != 1 or payload.get("release_status") != "disclosure_reviewed":
        errors.append("Association result payload must use reviewed schema version 1")
    if not isinstance(payload.get("generated_at"), str) or not payload.get("generated_at"):
        errors.append("Association result payload requires generated_at")
    else:
        try:
            generated_at = datetime.fromisoformat(payload["generated_at"].replace("Z", "+00:00"))
            if generated_at.tzinfo is None:
                errors.append("Association result generated_at must include a timezone")
        except ValueError:
            errors.append("Association result generated_at must be ISO-8601")
    families = payload.get("families")
    if not isinstance(families, list) or not families:
        errors.append("Association result payload must contain at least one approved family")
        return errors
    seen_families: set[str] = set()
    for family in families:
        if not isinstance(family, dict) or set(family) != RESULT_FAMILY_FIELDS:
            errors.append("Association family has missing or non-allowlisted fields")
            continue
        family_id = family.get("family_id")
        if not isinstance(family_id, str) or not family_id or family_id in seen_families:
            errors.append("Association family IDs must be unique nonblank strings")
        seen_families.add(str(family_id))
        rows = family.get("rows")
        family_size = family.get("family_size")
        if (not isinstance(rows, list) or not rows or isinstance(family_size, bool)
                or not isinstance(family_size, int) or family_size != len(rows)):
            errors.append(f"Association family {family_id} must publish its complete declared K")
            continue
        seen_ids: set[str] = set()
        family_p_values: list[float | None] = []
        for row in rows:
            if not isinstance(row, dict) or set(row) != RESULT_ROW_FIELDS:
                errors.append(f"Association family {family_id} contains a row with non-allowlisted fields")
                continue
            analysis_id = row.get("analysis_id")
            if not isinstance(analysis_id, str) or not analysis_id or analysis_id in seen_ids:
                errors.append(f"Association family {family_id} has duplicate or blank analysis IDs")
            seen_ids.add(str(analysis_id))
            if row.get("disclosure_status") != "approved_public_aggregate":
                errors.append(f"Association family {family_id} includes a row without disclosure approval")
            if row.get("variance_design") not in PUBLIC_VARIANCE_LABELS:
                errors.append(f"Association row {analysis_id} has an unsupported public variance-design label")
            if row.get("fit_status") not in {"success", "nonconvergence", "inestimable", "blocked_design_verification", "blocked_data_access", "blocked_measurement_rule", "code_error"}:
                errors.append(f"Association row {analysis_id} has unsupported fit_status")
            fit_status = row.get("fit_status")
            variance_design = row.get("variance_design")
            if fit_status == "success" and variance_design == "Design not fit-ready":
                errors.append(f"Successful association row {analysis_id} cannot be labeled Design not fit-ready")
            elif fit_status != "success" and variance_design != "Design not fit-ready":
                errors.append(f"Non-success association row {analysis_id} must be labeled Design not fit-ready")
            if row.get("fit_status") == "success":
                numeric: dict[str, float] = {}
                for field in ("estimate", "standard_error", "ci_lower", "ci_upper", "p_value", "q_value_by", "p_bonferroni", "n_model"):
                    value = row.get(field)
                    try:
                        number = float(value)
                    except (TypeError, ValueError):
                        errors.append(f"Association row {analysis_id} has invalid {field}")
                        continue
                    if not math.isfinite(number):
                        errors.append(f"Association row {analysis_id} has nonfinite {field}")
                    else:
                        numeric[field] = number
                for field in ("p_value", "q_value_by", "p_bonferroni"):
                    if field in numeric and not 0 <= numeric[field] <= 1:
                        errors.append(f"Association row {analysis_id} has out-of-range {field}")
                if "standard_error" in numeric and numeric["standard_error"] < 0:
                    errors.append(f"Association row {analysis_id} has negative standard_error")
                if "standard_error" in numeric and numeric["standard_error"] <= 0:
                    errors.append(f"Successful association row {analysis_id} requires positive standard_error")
                if "n_model" in numeric and (numeric["n_model"] < 0 or not numeric["n_model"].is_integer()):
                    errors.append(f"Association row {analysis_id} has invalid n_model")
                if ("ci_lower" in numeric and "ci_upper" in numeric
                        and numeric["ci_lower"] > numeric["ci_upper"]):
                    errors.append(f"Association row {analysis_id} has reversed confidence limits")
                family_p_values.append(numeric.get("p_value"))
            else:
                for field in ("estimate", "standard_error", "ci_lower", "ci_upper", "p_value", "q_value_by", "p_bonferroni", "n_model"):
                    if row.get(field) not in ("", None):
                        errors.append(f"Non-success association row {analysis_id} must not expose {field}")
                family_p_values.append(None)
        try:
            adjusted = adjust_pvalues(family_p_values)
        except (TypeError, ValueError) as exc:
            errors.append(f"Association family {family_id} has invalid p-values: {exc}")
            continue
        for index, row in enumerate(rows):
            if row.get("fit_status") != "success":
                continue
            for field, expected in (
                ("q_value_by", adjusted["q_value_by"][index]),
                ("p_bonferroni", adjusted["p_bonferroni"][index]),
            ):
                try:
                    observed = float(row.get(field))
                except (TypeError, ValueError):
                    continue  # The row-level numeric check reports this.
                if expected is None or not math.isclose(observed, expected, rel_tol=1e-9, abs_tol=1e-12):
                    errors.append(f"Association family {family_id} row {row.get('analysis_id')} has inconsistent {field}")
    return errors


def validate_payload(root: Path) -> list[str]:
    """Return validation errors for a browser-facing static site directory."""
    errors: list[str] = []
    if not root.is_dir():
        return [f"Site payload directory does not exist: {root}"]

    for required in ("index.html", "app.js"):
        if not (root / required).is_file() or (root / required).stat().st_size == 0:
            errors.append(f"Required site file is missing or empty: {required}")

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name not in ALLOWED_DOTFILES and path.suffix.lower() not in ALLOWED_SUFFIXES:
            errors.append(f"Unexpected non-site file type: {path.relative_to(root)}")
            continue
        if path.suffix.lower() == ".json":
            try:
                parsed = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                errors.append(f"Invalid JSON catalog {path.relative_to(root)}: {exc}")
                continue
            if path.name == "association_results_v1.json":
                errors.extend(
                    f"{path.relative_to(root)}: {error}"
                    for error in validate_association_payload(parsed)
                )
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("site-prototype/dist")
    errors = validate_payload(root)
    if errors:
        print("Public site payload validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Validated public site payload: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
