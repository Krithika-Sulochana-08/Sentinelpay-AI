def fuse_risk_scores(
    risk_result,
    behavior_result,
    graph_result,
    merchant_result
):
    """
    Combine transaction risk, behavioral anomaly risk,
    graph/relationship risk, and merchant-context risk
    into one unified decision score.
    """

    rule_score = risk_result["risk_score"]
    behavior_score = behavior_result["behavior_anomaly_score"]
    graph_score = graph_result["graph_risk_score"]
    merchant_score = merchant_result["merchant_context_score"]

    # Base weighted fusion
    fused_score = round(
        (0.35 * rule_score)
        + (0.25 * behavior_score)
        + (0.25 * graph_score)
        + (0.15 * merchant_score),
        2
    )

    # Strong coordinated-abuse evidence
    # must never remain low risk
    if graph_score >= 70:
        fused_score = max(fused_score, 75)

    # Moderate graph risk should force verification
    elif graph_score >= 35:
        fused_score = max(fused_score, 45)

    # Strong merchant-context anomaly should
    # require at least additional verification
    if merchant_score >= 50:
        fused_score = max(fused_score, 45)

    # Strong individual transaction or behavioral signals
    if rule_score >= 85 or behavior_score >= 90:
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
            "graph_risk_score": graph_score,
            "merchant_context_score": merchant_score
        }
    }