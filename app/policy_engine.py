ACTION_PRIORITY = {
    "ALLOW": 0,
    "CHALLENGE": 1,
    "REVIEW": 2,
    "BLOCK": 3
}


def resolve_final_action(fusion_result, cost_result):
    """
    Resolve risk-based and cost-based recommendations
    into one authoritative operational action.
    """

    risk_action = fusion_result["final_decision"]
    cost_action = cost_result["cost_optimized_action"]

    risk_priority = ACTION_PRIORITY.get(risk_action, 0)
    cost_priority = ACTION_PRIORITY.get(cost_action, 0)

    # Use the stronger intervention.
    if cost_priority > risk_priority:
        final_action = cost_action
        resolution_reason = (
            "Cost-aware analysis recommends a stronger intervention "
            "than the baseline risk policy."
        )

    elif risk_priority > cost_priority:
        final_action = risk_action
        resolution_reason = (
            "Risk policy requires a stronger intervention than the "
            "cost-optimized recommendation."
        )

    else:
        final_action = risk_action
        resolution_reason = (
            "Risk and cost-aware policies agree on the intervention."
        )

    return {
        "risk_recommended_action": risk_action,
        "cost_recommended_action": cost_action,
        "authoritative_action": final_action,
        "policy_resolution_reason": resolution_reason
    }