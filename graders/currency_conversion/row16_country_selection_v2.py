# graders/currency_conversion_v2/row16_country_selection_v2.py

from graders.currency_conversion.currency_lookup import get_country_entry_by_name
from graders.currency_conversion.utils import norm_unit


def _split_student_name(student_name: str):
    """
    Supports:
      - 'First Last'
      - 'First_Last'
      - 'First Middle Last'
      - 'First_Middle_Last'
    Returns: (first_name, last_name)
    """
    if not student_name:
        return "", ""

    s = str(student_name).strip()

    # Prefer underscore split if present (your pipeline uses First_Last)
    if "_" in s:
        parts = [p for p in s.split("_") if p]
    else:
        parts = [p for p in s.split() if p]

    if not parts:
        return "", ""

    first = parts[0]
    last = parts[-1] if len(parts) > 1 else parts[0]
    return first, last


def grade_row16_country_selection_v2(sheet, student_name: str):
    """
    Currency Conversion V2 — Row 16 (C16–F16)

    Rule:
      - C16, D16 must start with first two letters of FIRST name
      - E16, F16 must start with first two letters of LAST name
      - 0.5 pts each cell (max 2.0)
      - Country must exist on approved list (currency_lookup)

    Returns:
      (score: float, feedback: list[(code, params)], country_entries: list[entry_or_none])
    """

    first_name, last_name = _split_student_name(student_name)

    first = first_name.lower()
    last = last_name.lower()

    # Expected initials (fallback 'm' if name too short)
    expected_letters = [
        first[0] if len(first) > 0 else "m",
        first[1] if len(first) > 1 else "m",
        last[0] if len(last) > 0 else "m",
        last[1] if len(last) > 1 else "m",
    ]

    cells = ["C16", "D16", "E16", "F16"]

    score = 0.0
    feedback = []
    matched_entries = {}

    for cell, expected_letter in zip(cells, expected_letters):
        raw = sheet[cell].value
        country_name = norm_unit(raw) if raw else ""

        if not country_name:
            feedback.append(("CC16_COUNTRY_BLANK", {"cell": cell}))
            continue

        entry = get_country_entry_by_name(country_name)

        if not entry:
            feedback.append(("CC16_COUNTRY_NOT_APPROVED", {"cell": cell, "found": country_name}))
            continue

        canonical_country = entry["country"]

        if not canonical_country.lower().startswith(expected_letter.lower()):
            feedback.append((
                "CC16_COUNTRY_WRONG_INITIAL",
                {
                    "cell": cell,
                    "country": canonical_country,
                    "expected_letter": expected_letter.upper()
                }
            ))
            continue

        matched_entries[cell] = entry
        score += 0.5
        feedback.append((
            "CC16_COUNTRY_CORRECT",
            {
                "cell": cell,
                "country": canonical_country,
                "expected_letter": expected_letter.upper()
            }
        ))

    score = round(score, 1)

    # Summary message first
    if score == 2.0:
        feedback.insert(0, ("CC16_ALL_CORRECT", {"points": 2.0}))
    elif score > 0:
        feedback.insert(0, ("CC16_PARTIAL", {"earned": score, "possible": 2.0}))
    else:
        feedback.insert(0, ("CC16_NONE_CORRECT", {"possible": 2.0}))

    ordered_entries = [matched_entries.get(c) for c in cells]
    return score, feedback, ordered_entries
