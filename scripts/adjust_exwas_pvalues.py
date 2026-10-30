"""Apply family-wise Bonferroni and Benjamini–Yekutieli adjustments.

Pass one item per hypothesis in the complete, predeclared family for one
model family; use None when a hypothesis has no estimable p-value.
This function does not choose the family, fit models, read CHARLS data, or
adjust across multiple families.
"""
from __future__ import annotations

import math
from collections.abc import Sequence


def adjust_pvalues(p_values: Sequence[float | None]) -> dict[str, list[float | None]]:
    """Return order-preserving Bonferroni p-values and BY q-values.

    The caller must define the inferential family before looking at results
    and provide one item per hypothesis in that family. Use ``None`` for a
    predeclared hypothesis with no estimable p-value; it counts toward family
    size but receives no adjusted value. Do not remove hypotheses after seeing
    their results or convergence status.
    """
    raw_values = list(p_values)
    if not raw_values:
        return {"p_bonferroni": [], "q_value_by": []}
    values: list[float | None] = []
    for value in raw_values:
        if value is None:
            values.append(None)
            continue
        parsed = float(value)
        if not math.isfinite(parsed) or parsed < 0 or parsed > 1:
            raise ValueError("every supplied p-value must be finite and between 0 and 1")
        values.append(parsed)

    family_size = len(values)
    # Missing/unestimable hypotheses stay in K. For ranking, treat them as
    # p=1 (least favorable), but leave their own adjusted values blank.
    bonferroni = [min(1.0, value * family_size) if value is not None else None for value in values]
    harmonic = math.fsum(1.0 / rank for rank in range(1, family_size + 1))
    ordered = sorted(
        ((index, value if value is not None else 1.0) for index, value in enumerate(values)),
        key=lambda item: (item[1], item[0]),
    )
    q_values: list[float | None] = [None] * family_size
    running_minimum = 1.0
    for rank in range(family_size, 0, -1):
        index, value = ordered[rank - 1]
        adjusted = min(1.0, value * family_size * harmonic / rank)
        running_minimum = min(running_minimum, adjusted)
        if values[index] is not None:
            q_values[index] = running_minimum

    return {"p_bonferroni": bonferroni, "q_value_by": q_values}
