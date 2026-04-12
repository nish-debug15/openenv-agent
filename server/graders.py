class EasyGrader:
    def grade(self, predicted_severity=None, true_severity=None, steps=1, **kwargs) -> dict:
        breakdown, score = self._compute(predicted_severity, true_severity, steps)
        return {
            "score": score,
            "task_id": kwargs.get("task_id", 1),
            "episode_id": kwargs.get("episode_id", "unknown"),
            "scenario_id": kwargs.get("scenario_id", "unknown"),
            "breakdown": breakdown,
            "grader_version": "1.0.0"
        }

    def _compute(self, predicted_severity=None, true_severity=None, steps=1):
        breakdown = {
            "CORRECT_SEVERITY": 0.0,
            "CORRECT_SERVICE": 0.0,
            "CORRECT_PATTERN": 0.0,
            "TIME_BONUS_FAST": 0.0
        }
        if predicted_severity is None or true_severity is None:
            return breakdown, 0.05

        pred = str(predicted_severity).strip().lower()
        true = str(true_severity).strip().lower()
        try:
            s = max(1, int(steps))
        except (TypeError, ValueError):
            s = 1

        if pred == true:
            breakdown["CORRECT_SEVERITY"] = 0.40
            breakdown["CORRECT_SERVICE"]  = 0.30
            breakdown["CORRECT_PATTERN"]  = 0.15
            breakdown["TIME_BONUS_FAST"]  = 0.05 if s <= 1 else 0.0
            score = sum(breakdown.values())
        else:
            severity_map = {"mild": 0, "moderate": 1, "emergency": 2}
            if abs(severity_map.get(pred, 1) - severity_map.get(true, 1)) == 1:
                breakdown["CORRECT_SEVERITY"] = 0.20
                score = 0.30
            else:
                score = 0.05

        return breakdown, min(score, 0.95)


class MediumGrader:
    def grade(self, predicted_severity=None, true_severity=None, steps=1, **kwargs) -> dict:
        breakdown, score = self._compute(predicted_severity, true_severity, steps)
        return {
            "score": score,
            "task_id": kwargs.get("task_id", 1),
            "episode_id": kwargs.get("episode_id", "unknown"),
            "scenario_id": kwargs.get("scenario_id", "unknown"),
            "breakdown": breakdown,
            "grader_version": "1.0.0"
        }

    def _compute(self, predicted_severity=None, true_severity=None, steps=1):
        breakdown = {
            "CORRECT_SEVERITY": 0.0,
            "CORRECT_SERVICE": 0.0,
            "CORRECT_PATTERN": 0.0,
            "TIME_BONUS_FAST": 0.0
        }
        if predicted_severity is None or true_severity is None:
            return breakdown, 0.05

        pred = str(predicted_severity).strip().lower()
        true = str(true_severity).strip().lower()
        try:
            s = max(1, int(steps))
        except (TypeError, ValueError):
            s = 1

        if pred == true:
            breakdown["CORRECT_SEVERITY"] = 0.38
            breakdown["CORRECT_SERVICE"]  = 0.28
            breakdown["CORRECT_PATTERN"]  = 0.14
            breakdown["TIME_BONUS_FAST"]  = 0.05 if s <= 1 else 0.0
            score = sum(breakdown.values())
        else:
            severity_map = {"mild": 0, "moderate": 1, "emergency": 2}
            if abs(severity_map.get(pred, 1) - severity_map.get(true, 1)) == 1:
                breakdown["CORRECT_SEVERITY"] = 0.15
                score = 0.25
            else:
                score = 0.05

        return breakdown, min(score, 0.95)


class HardGrader:
    def grade(self, predicted_severity=None, true_severity=None, steps=1, **kwargs) -> dict:
        breakdown, score = self._compute(predicted_severity, true_severity, steps)
        return {
            "score": score,
            "task_id": kwargs.get("task_id", 1),
            "episode_id": kwargs.get("episode_id", "unknown"),
            "scenario_id": kwargs.get("scenario_id", "unknown"),
            "breakdown": breakdown,
            "grader_version": "1.0.0"
        }

    def _compute(self, predicted_severity=None, true_severity=None, steps=1):
        breakdown = {
            "CORRECT_SEVERITY": 0.0,
            "CORRECT_SERVICE": 0.0,
            "CORRECT_PATTERN": 0.0,
            "TIME_BONUS_FAST": 0.0
        }
        if predicted_severity is None or true_severity is None:
            return breakdown, 0.05

        pred = str(predicted_severity).strip().lower()
        true = str(true_severity).strip().lower()
        try:
            s = max(1, int(steps))
        except (TypeError, ValueError):
            s = 1

        if pred == true:
            breakdown["CORRECT_SEVERITY"] = 0.35
            breakdown["CORRECT_SERVICE"]  = 0.25
            breakdown["CORRECT_PATTERN"]  = 0.12
            breakdown["TIME_BONUS_FAST"]  = 0.05 if s <= 1 else 0.0
            score = sum(breakdown.values())
        else:
            severity_map = {"mild": 0, "moderate": 1, "emergency": 2}
            if abs(severity_map.get(pred, 1) - severity_map.get(true, 1)) == 1:
                breakdown["CORRECT_SEVERITY"] = 0.10
                score = 0.20
            else:
                score = 0.05

        return breakdown, min(score, 0.95)