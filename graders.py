from typing import Any

def grade(predicted_severity: Any = None, true_severity: Any = None, steps: Any = 1, **kwargs) -> float:
    if predicted_severity is None or true_severity is None:
        return 0.05
    pred = str(predicted_severity).strip().lower()
    true = str(true_severity).strip().lower()
    try:
        s = max(1, int(steps))
    except (TypeError, ValueError):
        s = 1
    if pred == true:
        return 0.95 if s <= 1 else (0.80 if s == 2 else 0.60)
    severity_map = {"mild": 0, "moderate": 1, "emergency": 2}
    if abs(severity_map.get(pred, 1) - severity_map.get(true, 1)) == 1:
        return 0.30
    return 0.05