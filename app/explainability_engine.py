def generate_explanation(
    transaction,
    risk_result,
    behavior_result,
    fusion_result,
    cost_result
):
    """
    Build a concise evidence-based explanation for the final SentinelPay decision.
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

    # Prioritize strongest evidence
    top_evidence = evidence[:5]

    final_decision = fusion_result["final_decision"]
    fused_score = fusion_result["fused_risk_score"]

    if final_decision == "ALLOW":
        summary = (
            "The transaction is currently assessed as low risk and can be allowed."
        )

    elif final_decision == "CHALLENGE":
        summary = (
            "The transaction shows moderate risk and should undergo additional verification."
        )

    else:
        summary = (
            "The transaction shows strong risk indicators and should be reviewed before approval."
        )

    return {
        "decision_summary": summary,
        "risk_score_explained": fused_score,
        "recommended_action": cost_result["cost_optimized_action"],
        "top_evidence": top_evidence,
        "explanation_confidence": "HIGH" if fused_score >= 75 else "MEDIUM"
    }