def fuse_risk_scores(risk_result, behavior_result, graph_result):
    """
    Combine transaction risk, behavioral anomaly risk,
    and graph/relationship risk into one final risk decision.
    """

    rule_score = risk_result["risk_score"]
    behavior_score = behavior_result["behavior_anomaly_score"]
    graph_score = graph_result["graph_risk_score"]

    # Base weighted fusion
    fused_score = round(
        (0.45 * rule_score)
        + (0.30 * behavior_score)
        + (0.25 * graph_score),
        2
    )

    # Strong coordinated-abuse evidence must never remain LOW risk
    if graph_score >= 70:
        fused_score = max(fused_score, 75)

    # Moderate relationship risk should force additional verification
    elif graph_score >= 35:
        fused_score = max(fused_score, 45)

    # Extremely high individual signals increase caution
    elif rule_score >= 85 or behavior_score >= 90:
        fused_score = min(fused_score + 8, 100)

    fused_score = min(round(fused_score, 2), 100)

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
            "behavior_anomaly_score": behavior_score,
            "graph_risk_score": graph_score
        }
    }