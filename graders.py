def grade(predicted_severity, true_severity, steps):
    score = 0.0
    if predicted_severity == true_severity:
        score += 0.7
    score += max(0, 0.3 - 0.05 * steps)
    score = min(score, 0.94)   
    score = max(score, 0.01)   
    return score