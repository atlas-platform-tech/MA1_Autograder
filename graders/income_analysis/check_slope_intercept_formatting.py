# graders/income_analysis/check_slope_intercept_formatting.py

def check_slope_intercept_formatting(ws):
    """
    Checks formatting of B30 (slope) and B31 (intercept).
    Correct formatting = number format with 0 decimal places.

    Returns:
        (score: float from 0 to 1,
         feedback: list[tuple[str, dict]])
    """
    slope_cell = ws["B30"]
    intercept_cell = ws["B31"]

    allowed_formats = [
        "0",
        "0_",
        "#,##0",
        "#,##0_",
        "0;-0;0",
        "#,##0;-#,##0;0"
    ]

    slope_fmt = slope_cell.number_format
    intercept_fmt = intercept_cell.number_format

    score = 0.0
    feedback = []

    if slope_fmt in allowed_formats:
        score += 0.5
        feedback.append(("IA_SLOPE_FORMAT_CORRECT", {"cell": "B30"}))
    else:
        feedback.append(("IA_SLOPE_FORMAT_INCORRECT", {"cell": "B30"}))

    if intercept_fmt in allowed_formats:
        score += 0.5
        feedback.append(("IA_INTERCEPT_FORMAT_CORRECT", {"cell": "B31"}))
    else:
        feedback.append(("IA_INTERCEPT_FORMAT_INCORRECT", {"cell": "B31"}))

    return score, feedback
