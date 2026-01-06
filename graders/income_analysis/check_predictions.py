# graders/income_analysis/check_predictions.py

def check_predictions(ws):
    """
    Check predicted values in E19–E35.

    Returns:
        (score: float, feedback: list[tuple[str, dict]])
    """
    total_rows = 17
    correct_count = 0

    for row in range(19, 36):
        formula = ws[f"E{row}"].value

        if isinstance(formula, str) and formula.startswith("="):
            normalized = (
                formula.replace("$", "")
                       .replace(" ", "")
                       .replace("(", "")
                       .replace(")", "")
                       .upper()
            )
            expected = f"=B30*D{row}+B31".upper()

            if normalized == expected:
                correct_count += 1

    if correct_count == total_rows:
        return 6.0, [("IA_PREDICTIONS_ALL_CORRECT", {"range": "E19:E35"})]

    if correct_count == 0:
        return 0.0, [("IA_PREDICTIONS_NONE_CORRECT", {"range": "E19:E35"})]

    score = round(correct_count * (6 / total_rows), 1)
    return score, [("IA_PREDICTIONS_PARTIAL", {"correct": correct_count, "total": total_rows, "range": "E19:E35"})]
