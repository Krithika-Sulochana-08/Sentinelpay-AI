from fastapi import FastAPI

from app.schemas import TransactionRequest
from app.risk_engine import calculate_risk
from app.behavior_engine import analyze_behavior
from app.graph_engine import analyze_graph_risk
from app.merchant_engine import analyze_merchant_context
from app.fusion_engine import fuse_risk_scores
from app.cost_engine import evaluate_decision_costs
from app.explainability_engine import generate_explanation
from app.drift_engine import update_drift_monitor
from app.policy_engine import resolve_final_action

app = FastAPI(
    title="SentinelPay AI",
    description="Explainable AI-powered payment risk intelligence system",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "application": "SentinelPay AI",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/risk/analyze")
def analyze_transaction(transaction: TransactionRequest):

    # 1. Transaction-level risk analysis
    risk_result = calculate_risk(transaction)

    # 2. Behavioral anomaly analysis
    behavior_result = analyze_behavior(transaction)

    # 3. Graph / relationship risk analysis
    graph_result = analyze_graph_risk(transaction)

    # 4. Merchant-context analysis
    merchant_result = analyze_merchant_context(transaction)

    # 5. Unified risk fusion
    fusion_result = fuse_risk_scores(
        risk_result,
        behavior_result,
        graph_result,
        merchant_result
    )

    # 6. Drift / fraud-spike monitoring
    drift_result = update_drift_monitor(
        fusion_result["fused_risk_score"]
    )

    # 7. Cost-aware decision analysis
    cost_result = evaluate_decision_costs(
        transaction,
        fusion_result["fused_risk_score"]
    )

    policy_result = resolve_final_action(
    fusion_result,
    cost_result
    )
    # 8. Explainability
    explanation_result = generate_explanation(
        transaction,
        risk_result,
        behavior_result,
        graph_result,
        merchant_result,
        fusion_result,
        cost_result
    )

    # 9. API response
    return {
        "transaction_id": transaction.transaction_id,
        "merchant_id": transaction.merchant_id,

        # Transaction risk
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "decision": risk_result["decision"],
        "reasons": risk_result["reasons"],

        # Behavioral risk
        "behavior_anomaly_score": behavior_result[
            "behavior_anomaly_score"
        ],
        "behavior_status": behavior_result["behavior_status"],
        "amount_deviation_ratio": behavior_result[
            "amount_deviation_ratio"
        ],
        "behavior_signals": behavior_result["behavior_signals"],

        # Graph intelligence
        "graph_risk_score": graph_result["graph_risk_score"],
        "graph_status": graph_result["graph_status"],
        "graph_signals": graph_result["graph_signals"],
        "linked_account_counts": graph_result[
            "linked_account_counts"
        ],

        # Merchant context
        "merchant_context_score": merchant_result[
            "merchant_context_score"
        ],
        "merchant_context_status": merchant_result[
            "merchant_context_status"
        ],
        "merchant_category": merchant_result["merchant_category"],
        "merchant_amount_ratio": merchant_result[
            "merchant_amount_ratio"
        ],
        "merchant_signals": merchant_result["merchant_signals"],

        # Unified risk
        "fused_risk_score": fusion_result["fused_risk_score"],
        "final_risk_level": fusion_result["final_risk_level"],
        "final_decision": fusion_result["final_decision"],
        "fusion_components": fusion_result["fusion_components"],

        # Cost-aware decisioning
        "estimated_action_costs": cost_result[
            "estimated_action_costs"
        ],
        "cost_optimized_action": cost_result[
            "cost_optimized_action"
        ],
        "minimum_expected_cost": cost_result[
            "minimum_expected_cost"
        ],

        "risk_recommended_action": policy_result[
            "risk_recommended_action"
        ],
        "cost_recommended_action": policy_result[
            "cost_recommended_action"
        ],
        "authoritative_action": policy_result[
            "authoritative_action"
        ],
        "policy_resolution_reason": policy_result[
            "policy_resolution_reason"
        ],

        # Explainability
        "decision_summary": explanation_result[
            "decision_summary"
        ],
        "recommended_action": explanation_result[
            "recommended_action"
        ],
        "top_evidence": explanation_result["top_evidence"],
        "explanation_confidence": explanation_result[
            "explanation_confidence"
        ],

        # Drift monitoring
        "drift_status": drift_result["drift_status"],
        "recent_average_risk": drift_result[
            "recent_average_risk"
        ],
        "high_risk_ratio": drift_result["high_risk_ratio"],
        "fraud_spike_detected": drift_result[
            "fraud_spike_detected"
        ]
    }