import json

from app.schemas import TransactionRequest
from app.risk_engine import calculate_risk
from app.behavior_engine import analyze_behavior
from app.graph_engine import analyze_graph_risk
from app.merchant_engine import analyze_merchant_context
from app.fusion_engine import fuse_risk_scores
from app.cost_engine import evaluate_decision_costs
from app.policy_engine import resolve_final_action
from app.evaluation_engine import evaluate_predictions


def run_sentinelpay_prediction(transaction_data):
    """
    Run one held-out transaction through SentinelPay
    and convert the authoritative action into a binary prediction.

    0 = LEGITIMATE / ALLOW
    1 = FRAUD-RISK / intervention required
    """

    transaction = TransactionRequest(
        **transaction_data
    )

    risk_result = calculate_risk(
        transaction
    )

    behavior_result = analyze_behavior(
        transaction
    )

    # Read-only graph evaluation prevents the held-out
    # test from changing SentinelPay's live graph state.
    graph_result = analyze_graph_risk(
        transaction,
        update_state=False
    )

    merchant_result = analyze_merchant_context(
        transaction
    )

    fusion_result = fuse_risk_scores(
        risk_result,
        behavior_result,
        graph_result,
        merchant_result
    )

    cost_result = evaluate_decision_costs(
        transaction,
        fusion_result["fused_risk_score"]
    )

    policy_result = resolve_final_action(
        fusion_result,
        cost_result
    )

    authoritative_action = policy_result[
        "authoritative_action"
    ]

    predicted_label = (
        0
        if authoritative_action == "ALLOW"
        else 1
    )

    return {
        "transaction_id":
            transaction.transaction_id,

        "fused_risk_score":
            fusion_result[
                "fused_risk_score"
            ],

        "risk_level":
            fusion_result[
                "final_risk_level"
            ],

        "authoritative_action":
            authoritative_action,

        "predicted_label":
            predicted_label
    }


with open(
    "data/heldout_transactions.json",
    "r",
    encoding="utf-8"
) as file:
    heldout_data = json.load(
        file
    )


y_true = []
y_pred = []
transaction_amounts = []


print(
    "\nSentinelPay Actual Held-Out Evaluation"
)
print(
    "=" * 60
)


for item in heldout_data:

    actual_label = item[
        "label"
    ]

    transaction_data = item[
        "transaction"
    ]

    prediction = (
        run_sentinelpay_prediction(
            transaction_data
        )
    )

    y_true.append(
        actual_label
    )

    y_pred.append(
        prediction[
            "predicted_label"
        ]
    )

    transaction_amounts.append(
        transaction_data[
            "amount"
        ]
    )

    print(
        f"\nTransaction: "
        f"{prediction['transaction_id']}"
    )

    print(
        f"Actual label: "
        f"{actual_label}"
    )

    print(
        f"Predicted label: "
        f"{prediction['predicted_label']}"
    )

    print(
        f"Fused risk score: "
        f"{prediction['fused_risk_score']}"
    )

    print(
        f"Risk level: "
        f"{prediction['risk_level']}"
    )

    print(
        f"Action: "
        f"{prediction['authoritative_action']}"
    )


results = evaluate_predictions(
    y_true=y_true,
    y_pred=y_pred,
    transaction_amounts=transaction_amounts
)


print(
    "\n" + "=" * 60
)

print(
    "SentinelPay Evaluation Metrics"
)

print(
    "=" * 60
)


for key, value in results.items():
    print(
        f"{key}: {value}"
    )