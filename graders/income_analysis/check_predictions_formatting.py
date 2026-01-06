# graders/income_analysis/check_predictions_formatting.py

def check_currency_formatting(ws):
    """
    Check formatting of predicted values E19–E35.
    Expected: currency with 0 decimal places.

    Returns:
        (score: float, feedback: list[tuple[str, dict]])
    """
    total_rows = 17
    correct_count = 0

    acceptable_formats = [
        "$#,##0",
        '"$"#,##0',
        '$#,##0_);($#,##0)',
        '"$"#,##0_);("$"#,##0)'
    ]

    for row in range(19, 36):
        cell = ws[f"E{row}"]
        fmt = cell.number_format
        if fmt in acceptable_formats:
            correct_count += 1

    if correct_count == total_rows:
        return 1.0, [("IA_PRED_FORMAT_ALL_CORRECT", {"range": "E19:E35"})]

    if correct_count == 0:
        return 0.0, [("IA_PRED_FORMAT_NONE_CORRECT", {"range": "E19:E35"})]

    score = round(correct_count / total_rows, 2)
    return score, [("IA_PRED_FORMAT_PARTIAL", {"correct": correct_count, "total": total_rows, "range": "E19:E35"})]
