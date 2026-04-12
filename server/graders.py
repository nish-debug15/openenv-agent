class EasyGrader:
    def grade(self, predicted_severity=None, true_severity=None, steps=1, **kwargs) -> float:
        if predicted_severity is None or true_severity is None:
            return 0.05
        pred = str(predicted_severity).strip().lower()
        true = str(true_severity).strip().lower()
        try:
            s = max(1, int(steps))
        except (TypeError, ValueError):
            s = 1
        if pred == true:
            return 0.95 if s <= 1 else (0.80 if s == 2 else 0.65)
        severity_map = {"mild": 0, "moderate": 1, "emergency": 2}
        if abs(severity_map.get(pred, 1) - severity_map.get(true, 1)) == 1:
            return 0.30
        return 0.05


class MediumGrader:
    def grade(self, predicted_severity=None, true_severity=None, steps=1, **kwargs) -> float:
        if predicted_severity is None or true_severity is None:
            return 0.05
        pred = str(predicted_severity).strip().lower()
        true = str(true_severity).strip().lower()
        try:
            s = max(1, int(steps))
        except (TypeError, ValueError):
            s = 1
        if pred == true:
            return 0.90 if s <= 1 else (0.75 if s == 2 else 0.60)
        severity_map = {"mild": 0, "moderate": 1, "emergency": 2}
        if abs(severity_map.get(pred, 1) - severity_map.get(true, 1)) == 1:
            return 0.25
        return 0.05


class HardGrader:
    def grade(self, predicted_severity=None, true_severity=None, steps=1, **kwargs) -> float:
        if predicted_severity is None or true_severity is None:
            return 0.05
        pred = str(predicted_severity).strip().lower()
        true = str(true_severity).strip().lower()
        try:
            s = max(1, int(steps))
        except (TypeError, ValueError):
            s = 1
        if pred == true:
            return 0.85 if s <= 1 else (0.70 if s == 2 else 0.55)
        severity_map = {"mild": 0, "moderate": 1, "emergency": 2}
        if abs(severity_map.get(pred, 1) - severity_map.get(true, 1)) == 1:
            return 0.20
        return 0.05