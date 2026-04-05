def grade(predicted_severity, true_severity, steps):
    score = 0.0

    if predicted_severity == true_severity:
        score += 0.7

    # Penalize too many steps
    score += max(0, 0.3 - 0.05 * steps)

    return min(score, 1.0)
