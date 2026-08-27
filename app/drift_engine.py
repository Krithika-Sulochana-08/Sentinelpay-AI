recent_scores = []


def update_drift_monitor(fused_score):
    """
    Track recent fused risk scores and detect sudden fraud-risk spikes.
    """

    recent_scores.append(fused_score)

    # Keep only the latest 20 transactions
    if len(recent_scores) > 20:
        recent_scores.pop(0)

    current_window_size = len(recent_scores)

    if current_window_size < 5:
        return {
            "drift_status": "INSUFFICIENT_DATA",
            "recent_average_risk": round(
                sum(recent_scores) / current_window_size,
                2
            ),
            "high_risk_ratio": 0.0,
            "fraud_spike_detected": False
        }

    recent_average = sum(recent_scores) / current_window_size

    high_risk_count = sum(
        1 for score in recent_scores
        if score >= 75
    )

    high_risk_ratio = high_risk_count / current_window_size

    fraud_spike_detected = False
    drift_status = "STABLE"

    # Spike rule:
    # At least 40% of recent transactions are high risk
    if high_risk_ratio >= 0.40:
        fraud_spike_detected = True
        drift_status = "HIGH_RISK_SPIKE"

    # Elevated overall risk even if not enough are HIGH
    elif recent_average >= 55:
        drift_status = "ELEVATED_RISK"

    return {
        "drift_status": drift_status,
        "recent_average_risk": round(recent_average, 2),
        "high_risk_ratio": round(high_risk_ratio, 2),
        "fraud_spike_detected": fraud_spike_detected
    }