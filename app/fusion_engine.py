def fuse_risk_scores(risk_result, behavior_result):
    """
    Combine transaction-rule risk and behavioral anomaly risk
    into a single adaptive decision score.
    """

    rule_score = risk_result["risk_score"]
    behavior_score = behavior_result["behavior_anomaly_score"]

    # Weighted fusion
    # Rule engine gets slightly more weight initially because
    # it directly represents transaction-level risk conditions.
    fused_score = round(
        (0.6 * rule_score) + (0.4 * behavior_score),
        2
    )

    # Adaptive escalation:
    # If either engine is extremely concerned, increase caution.
    if rule_score >= 85 or behavior_score >= 90:
        fused_score = min(fused_score + 8, 100)

    # Final intervention policy
    if fused_score >= 75:
        final_risk_level = "HIGH"
        final_decision = "REVIEW"

    elif fused_score >= 45:
        final_risk_level = "MEDIUM"
        final_decision = "CHALLENGE"

    else:
        final_risk_level = "LOW"
        final_decision = "ALLOW"

    return {
        "fused_risk_score": fused_score,
        "final_risk_level": final_risk_level,
        "final_decision": final_decision,
        "fusion_components": {
            "transaction_rule_score": rule_score,
            "behavior_anomaly_score": behavior_score
        }
    }