def analyze_confidence(
    risk_result,
    behavior_result,
    graph_result,
    merchant_result
):
    """
    Estimate decision confidence from agreement between
    SentinelPay's major risk signals.

    This is a transparent rule-based uncertainty measure,
    not probabilistic or ML-calibrated uncertainty.
    """

    scores = [
        risk_result["risk_score"],
        behavior_result["behavior_anomaly_score"],
        graph_result["graph_risk_score"],
        merchant_result["merchant_context_score"]
    ]

    # Measure disagreement using the spread between signals
    score_range = max(scores) - min(scores)

    # Convert disagreement into a 0-100 uncertainty score
    uncertainty_score = round(score_range, 2)

    if uncertainty_score <= 20:
        signal_agreement = "STRONG"
        decision_confidence = "HIGH"

    elif uncertainty_score <= 50:
        signal_agreement = "MIXED"
        decision_confidence = "MEDIUM"

    else:
        signal_agreement = "WEAK"
        decision_confidence = "LOW"

    # Recommend human review when signals conflict strongly
    human_review_recommended = uncertainty_score > 50

    return {
        "decision_confidence": decision_confidence,
        "uncertainty_score": uncertainty_score,
        "signal_agreement": signal_agreement,
        "human_review_recommended": human_review_recommended,
        "signal_scores": {
            "transaction_rule_score": scores[0],
            "behavior_anomaly_score": scores[1],
            "graph_risk_score": scores[2],
            "merchant_context_score": scores[3]
        }
    }