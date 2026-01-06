# graders/income_analysis/check_slope_intercept.py

def check_slope_intercept(ws):
    """
    Check the slope and intercept formulas in B30 and B31.

    Returns:
        (score: int, feedback: list[tuple[str, dict]])
    """
    slope_cell = ws["B30"]
    intercept_cell = ws["B31"]

    slope_formula = slope_cell.value.strip().replace(" ", "").upper() if isinstance(slope_cell.value, str) else ""
    intercept_formula = intercept_cell.value.strip().replace(" ", "").upper() if isinstance(intercept_cell.value, str) else ""

    score = 0
    feedback = []

    correct_slope = "=SLOPE(B19:B26,A19:A26)"
    correct_intercept = "=INTERCEPT(B19:B26,A19:A26)"
    reversed_slope = "=SLOPE(A19:A26,B19:B26)"
    reversed_intercept = "=INTERCEPT(A19:A26,B19:B26)"

    # ----- Slope -----
    if slope_formula == correct_slope:
        score += 3
        feedback.append(("IA_SLOPE_CORRECT", {"cell": "B30"}))
    elif slope_formula == reversed_slope:
        score += 2
        feedback.append(("IA_SLOPE_REVERSED", {"cell": "B30"}))
    elif "SLOPE(" in slope_formula:
        score += 1
        feedback.append(("IA_SLOPE_WRONG_RANGE", {"cell": "B30"}))
    else:
        feedback.append(("IA_SLOPE_MISSING", {"cell": "B30"}))

    # ----- Intercept -----
    if intercept_formula == correct_intercept:
        score += 3
        feedback.append(("IA_INTERCEPT_CORRECT", {"cell": "B31"}))
    elif intercept_formula == reversed_intercept:
        score += 2
        feedback.append(("IA_INTERCEPT_REVERSED", {"cell": "B31"}))
    elif "INTERCEPT(" in intercept_formula:
        score += 1
        feedback.append(("IA_INTERCEPT_WRONG_RANGE", {"cell": "B31"}))
    else:
        feedback.append(("IA_INTERCEPT_MISSING", {"cell": "B31"}))

    return score, feedback
