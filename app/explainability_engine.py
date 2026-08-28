def generate_explanation(
    transaction,
    risk_result,
    behavior_result,
    graph_result,
    merchant_result,
    fusion_result,
    cost_result
):
    """
    Build a concise evidence-based explanation
    for the final SentinelPay decision.
    """

    evidence = []

    # Transaction-level evidence
    for reason in risk_result.get("reasons", []):
        evidence.append({
            "source": "transaction_risk",
            "evidence": reason
        })

    # Behavioral evidence
    for signal in behavior_result.get("behavior_signals", []):
        evidence.append({
            "source": "behavior",
            "evidence": signal
        })

    # Graph / relationship evidence
    for signal in graph_result.get("graph_signals", []):
        evidence.append({
            "source": "graph_intelligence",
            "evidence": signal
        })

    # Merchant-context evidence
    for signal in merchant_result.get("merchant_signals", []):
        evidence.append({
            "source": "merchant_context",
            "evidence": signal
        })

    # Add merchant amount-ratio evidence when anomalous
    merchant_ratio = merchant_result.get("merchant_amount_ratio")

    if (
        merchant_ratio is not None
        and merchant_result.get("merchant_context_score", 0) > 0
    ):
        evidence.append({
            "source": "merchant_context",
            "evidence": (
                f"Transaction amount is {merchant_ratio}x "
                "the merchant's typical amount"
            )
        })

    # Remove neutral statements when stronger evidence exists
    top_evidence = [
        item for item in evidence
        if item["evidence"] != "No major risk indicators detected"
    ][:5]

    if not top_evidence:
        top_evidence = [{
            "source": "transaction_risk",
            "evidence": "No major risk indicators detected"
        }]

    final_decision = fusion_result["final_decision"]
    fused_score = fusion_result["fused_risk_score"]

    if final_decision == "ALLOW":
        summary = (
            "The transaction is currently assessed as low risk "
            "and can be allowed."
        )

    elif final_decision == "CHALLENGE":
        summary = (
            "The transaction shows moderate risk and should "
            "undergo additional verification."
        )

    else:
        summary = (
            "The transaction shows strong risk indicators and "
            "should be reviewed before approval."
        )

    # Explanation confidence
    if fused_score >= 75:
        confidence = "HIGH"
    elif fused_score >= 40:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "decision_summary": summary,
        "risk_score_explained": fused_score,
        "recommended_action": cost_result[
            "cost_optimized_action"
        ],
        "top_evidence": top_evidence,
        "explanation_confidence": confidence
    }