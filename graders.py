"""
Grader for the Medical Triage RL Environment.

CONTRACT: grade() MUST return a float strictly in (0.0, 1.0).
Values of exactly 0.0 or 1.0 will be REJECTED by the OpenEnv validator.

Scoring design:
  - Correct, 1 step:  0.88  (fast + right = best)
  - Correct, 2 steps: 0.82
  - Correct, 3 steps: 0.76
  - Correct, 4+ steps: 0.70 (floor for correct)
  - Adjacent error (Moderate↔Emergency or Mild↔Moderate): 0.28–0.35
  - Opposite error (Mild vs Emergency): 0.05 (clinically dangerous)
  - All values clamped to [0.03, 0.97] — never touching 0.0 or 1.0
"""

from __future__ import annotations

# Ordinal severity mapping for partial credit
_SEVERITY_RANK: dict[str, int] = {
    "Mild":      0,
    "Moderate":  1,
    "Emergency": 2,
}


def grade(predicted_severity: str, true_severity: str, steps: int) -> float:
    """
    Score a single triage episode.

    Args:
        predicted_severity: Agent's final prediction ("Mild" / "Moderate" / "Emergency")
        true_severity:       Ground-truth severity label
        steps:               Total steps taken (including request_more_info steps)

    Returns:
        float strictly in (0.0, 1.0)
    """
    steps = max(int(steps), 1)

    pred_rank = _SEVERITY_RANK.get(predicted_severity, 1)
    true_rank = _SEVERITY_RANK.get(true_severity, 1)
    distance  = abs(pred_rank - true_rank)   # 0 = exact, 1 = adjacent, 2 = opposite

    if distance == 0:
        # Exact match — reward speed
        # Steps: 1→0.88, 2→0.82, 3→0.76, 4+→0.70
        speed_bonus = max(0.0, 0.18 - 0.06 * (steps - 1))
        score = 0.70 + speed_bonus

    elif distance == 1:
        # Adjacent level — partial credit (clinically defensible error)
        # Under-triaging Emergency→Moderate is penalised more than over-triaging
        if true_rank == 2 and pred_rank == 1:   # Emergency predicted as Moderate
            base = 0.22
        elif true_rank == 1 and pred_rank == 2:  # Moderate predicted as Emergency
            base = 0.30                          # over-triage: safer but wasteful
        else:
            base = 0.26                          # Mild↔Moderate
        speed_bonus = max(0.0, 0.05 - 0.01 * (steps - 1))
        score = base + speed_bonus

    else:
        # Opposite ends (Mild vs Emergency) — dangerous, minimal score
        score = 0.05

    # Hard clamp: NEVER return 0.0 or 1.0
    score = max(0.03, min(0.97, float(score)))
    return round(score, 4)