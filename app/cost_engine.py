def evaluate_decision_costs(transaction, fused_score):
    """
    Estimate the expected business cost of each possible action.
    """

    fraud_probability = fused_score / 100.0
    legitimate_probability = 1.0 - fraud_probability

    amount = transaction.amount

    # Simple baseline assumptions
    review_cost = 25.0
    challenge_cost = 10.0

    # Expected cost if payment is allowed
    allow_cost = fraud_probability * amount

    # Challenge reduces some fraud but introduces customer friction
    challenge_cost_expected = (
        fraud_probability * amount * 0.35
        + legitimate_probability * challenge_cost
    )

    # Manual review catches most fraud but costs analyst effort
    review_cost_expected = (
        fraud_probability * amount * 0.15
        + review_cost
    )

    # Blocking avoids fraud loss but can reject legitimate revenue
    block_cost = legitimate_probability * amount

    costs = {
        "ALLOW": round(allow_cost, 2),
        "CHALLENGE": round(challenge_cost_expected, 2),
        "REVIEW": round(review_cost_expected, 2),
        "BLOCK": round(block_cost, 2)
    }

    recommended_action = min(costs, key=costs.get)

    return {
        "estimated_action_costs": costs,
        "cost_optimized_action": recommended_action,
        "minimum_expected_cost": costs[recommended_action]
    }