from copy import deepcopy

from app.risk_engine import calculate_risk
from app.behavior_engine import analyze_behavior
from app.graph_engine import analyze_graph_risk
from app.merchant_engine import analyze_merchant_context
from app.fusion_engine import fuse_risk_scores
from app.cost_engine import evaluate_decision_costs
from app.policy_engine import resolve_final_action


def run_counterfactual_analysis(transaction):
    """
    Generate what-if scenarios by modifying
    high-impact transaction attributes and re-running
    SentinelPay's decision pipeline.

    This is deterministic counterfactual analysis,
    not causal inference.
    """

    scenarios = []

    # Base transaction as mutable dictionary
    base_data = transaction.model_dump()

    # Scenario 1: known device
    if transaction.is_new_device:
        scenario_data = deepcopy(base_data)
        scenario_data["is_new_device"] = False

        result = _evaluate_scenario(
            transaction,
            scenario_data
        )

        scenarios.append({
            "scenario": "KNOWN_DEVICE",
            "change": (
                "Treat transaction as coming "
                "from a known device"
            ),
            **result
        })

    # Scenario 2: mature account
    if transaction.account_age_days < 30:
        scenario_data = deepcopy(base_data)
        scenario_data["account_age_days"] = 180

        result = _evaluate_scenario(
            transaction,
            scenario_data
        )

        scenarios.append({
            "scenario": "MATURE_ACCOUNT",
            "change": "Treat customer account as mature",
            **result
        })

    # Scenario 3: normal transaction velocity
    if transaction.transactions_last_1h > 3:
        scenario_data = deepcopy(base_data)

        scenario_data["transactions_last_1h"] = 1
        scenario_data["transactions_last_24h"] = min(
            transaction.transactions_last_24h,
            3
        )

        result = _evaluate_scenario(
            transaction,
            scenario_data
        )

        scenarios.append({
            "scenario": "NORMAL_VELOCITY",
            "change": (
                "Reduce transaction velocity "
                "to normal levels"
            ),
            **result
        })

    # Scenario 4: amount closer to historical average
    if transaction.avg_transaction_amount_30d > 0:
        ratio = (
            transaction.amount
            / transaction.avg_transaction_amount_30d
        )

        if ratio >= 3:
            scenario_data = deepcopy(base_data)

            scenario_data["amount"] = round(
                transaction.avg_transaction_amount_30d * 1.5,
                2
            )

            result = _evaluate_scenario(
                transaction,
                scenario_data
            )

            scenarios.append({
                "scenario": "NORMALIZED_AMOUNT",
                "change": (
                    "Reduce amount closer to the customer's "
                    "historical average"
                ),
                **result
            })

    # Scenario 5: combined safer profile
    combined_data = deepcopy(base_data)
    combined_changes = []

    if transaction.is_new_device:
        combined_data["is_new_device"] = False
        combined_changes.append("known device")

    if transaction.account_age_days < 30:
        combined_data["account_age_days"] = 180
        combined_changes.append("mature account")

    if transaction.transactions_last_1h > 3:
        combined_data["transactions_last_1h"] = 1
        combined_data["transactions_last_24h"] = min(
            transaction.transactions_last_24h,
            3
        )
        combined_changes.append("normal velocity")

    if transaction.avg_transaction_amount_30d > 0:
        ratio = (
            transaction.amount
            / transaction.avg_transaction_amount_30d
        )

        if ratio >= 3:
            combined_data["amount"] = round(
                transaction.avg_transaction_amount_30d * 1.5,
                2
            )

            combined_changes.append(
                "amount near historical average"
            )

    if combined_changes:
        result = _evaluate_scenario(
            transaction,
            combined_data
        )

        scenarios.append({
            "scenario": "COMBINED_SAFER_PROFILE",
            "change": (
                "Simulate: "
                + ", ".join(combined_changes)
            ),
            **result
        })

    # Sort scenarios by strongest risk reduction
    scenarios.sort(
        key=lambda item: item["risk_reduction"],
        reverse=True
    )

    return {
        "counterfactuals_available": len(scenarios) > 0,
        "counterfactual_scenarios": scenarios[:5]
    }


def _evaluate_scenario(
    original_transaction,
    scenario_data
):
    """
    Re-run SentinelPay on one modified scenario.

    Graph analysis is read-only so counterfactual
    simulations do not contaminate the live graph.
    """

    scenario_transaction = (
        original_transaction.__class__(
            **scenario_data
        )
    )

    # Counterfactual transaction analysis
    risk_result = calculate_risk(
        scenario_transaction
    )

    behavior_result = analyze_behavior(
        scenario_transaction
    )

    # Read-only graph analysis
    graph_result = analyze_graph_risk(
        scenario_transaction,
        update_state=False
    )

    merchant_result = analyze_merchant_context(
        scenario_transaction
    )

    fusion_result = fuse_risk_scores(
        risk_result,
        behavior_result,
        graph_result,
        merchant_result
    )

    cost_result = evaluate_decision_costs(
        scenario_transaction,
        fusion_result["fused_risk_score"]
    )

    policy_result = resolve_final_action(
        fusion_result,
        cost_result
    )

    # Original transaction analysis for comparison
    original_risk = calculate_risk(
        original_transaction
    )

    original_behavior = analyze_behavior(
        original_transaction
    )

    # Original graph comparison is also read-only
    original_graph = analyze_graph_risk(
        original_transaction,
        update_state=False
    )

    original_merchant = analyze_merchant_context(
        original_transaction
    )

    original_fusion = fuse_risk_scores(
        original_risk,
        original_behavior,
        original_graph,
        original_merchant
    )

    # Measure change in fused risk
    risk_reduction = round(
        original_fusion["fused_risk_score"]
        - fusion_result["fused_risk_score"],
        2
    )

    return {
        "counterfactual_fused_risk_score": (
            fusion_result["fused_risk_score"]
        ),
        "counterfactual_risk_level": (
            fusion_result["final_risk_level"]
        ),
        "counterfactual_action": (
            policy_result["authoritative_action"]
        ),
        "risk_reduction": risk_reduction
    }