from __future__ import annotations

_SEVERITY_RANK: dict[str, int] = {
    "Mild":      0,
    "Moderate":  1,
    "Emergency": 2,
}


def grade(predicted_severity: str, true_severity: str, steps: int) -> float:
    steps = max(int(steps), 1)

    pred_rank = _SEVERITY_RANK.get(predicted_severity, 1)
    true_rank = _SEVERITY_RANK.get(true_severity, 1)
    distance  = abs(pred_rank - true_rank)

    if distance == 0:
        speed_bonus = max(0.0, 0.18 - 0.06 * (steps - 1))
        score = 0.70 + speed_bonus

    elif distance == 1:
        if true_rank == 2 and pred_rank == 1:
            base = 0.22
        elif true_rank == 1 and pred_rank == 2:
            base = 0.30
        else:
            base = 0.26
        speed_bonus = max(0.0, 0.05 - 0.01 * (steps - 1))
        score = base + speed_bonus

    else:
        score = 0.05

    score = max(0.04, min(0.96, float(score)))
    return score