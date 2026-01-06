# graders/unit_conversions/temp_conversions_v2.py

from graders.unit_conversions.utils import norm_formula


def grade_temp_conversions_v2(sheet):
    """
    V2 JSON-driven strict grader for temperature conversions on the Unit Conversions tab.
    
    Checks:
      • C40 = (5/9)*(A40-32)
      • A41 = (9/5)*C41 + 32
    Accepts parentheses, spacing differences, and reordered but equivalent expressions.
    """

    # ----------------------- Score buckets -----------------------
    score = 0        # 4 points max (2 for each formula)
    feedback = []    # list of (code, params)

    # ----------------------- Extract and normalize -----------------------
    c40 = norm_formula(sheet["C40"].value)
    a41 = norm_formula(sheet["A41"].value)

    # C40 requirements
    required_c40 = {
        "A40-32",
        "5/9"
    }

    # A41 requirements
    required_a41 = {
        "C41",
        "9/5",
        "+32"
    }

    # ============================================================
    # 1. Grade C40 formula
    # ============================================================

    c40_ok = (
        isinstance(c40, str) and
        c40.startswith("=") and
        "*" in c40 and
        all(fragment in c40 for fragment in required_c40)
    )

    if c40_ok:
        score += 2
        feedback.append(("UC_TEMP_C40_CORRECT", {"cell": "C40"}))
    else:
        feedback.append(("UC_TEMP_C40_INCORRECT",
                         {"cell": "C40", "required": list(required_c40)}))

    # ============================================================
    # 2. Grade A41 formula
    # ============================================================

    a41_ok = (
        isinstance(a41, str) and
        a41.startswith("=") and
        "*" in a41 and
        all(fragment in a41 for fragment in required_a41)
    )

    if a41_ok:
        score += 2
        feedback.append(("UC_TEMP_A41_CORRECT", {"cell": "A41"}))
    else:
        feedback.append(("UC_TEMP_A41_INCORRECT",
                         {"cell": "A41", "required": list(required_a41)}))

    # ============================================================
    # 3. Clamp and return V2 structured output
    # ============================================================

    return {
        "temp_and_celsius_score": min(score, 4),
        "temp_and_celsius_feedback": feedback
    }
