def grade(predicted_severity, true_severity, steps):
    score = 0.0

    if predicted_severity == true_severity:
        score += 0.8
    elif true_severity == "Emergency":
        # Severe penalty for under-triage
        if predicted_severity == "Moderate":
            score -= 0.5
        elif predicted_severity == "Mild":
            score -= 1.0
    elif true_severity == "Moderate":
        if predicted_severity == "Emergency":
            score += 0.4 # Over-triage is preferable to under-triage
        elif predicted_severity == "Mild":
            score -= 0.4
    elif true_severity == "Mild":
        if predicted_severity == "Emergency":
            score += 0.0 # Extreme over-triage, neutral but not rewarded
        elif predicted_severity == "Moderate":
            score += 0.3 # Safe over-triage

    # Penalize too many steps (e.g., asking for more info too much)
    score -= 0.05 * steps

    # Clamp the final score between 0.0 and 1.0
    return max(0.0, min(score, 1.0))
