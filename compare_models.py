import json

from app.schemas import TransactionRequest

from app.risk_engine import calculate_risk
from app.behavior_engine import analyze_behavior
from app.graph_engine import analyze_graph_risk
from app.merchant_engine import analyze_merchant_context
from app.fusion_engine import fuse_risk_scores

from app.ml_engine import (
    train_ml_model,
    predict_ml_label
)

from app.hybrid_engine import (
    calculate_hybrid_risk
)

from app.evaluation_engine import (
    evaluate_predictions
)


def load_dataset(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


training_data = load_dataset(
    "data/training_transactions.json"
)

heldout_data = load_dataset(
    "data/heldout_transactions.json"
)


# ---------------------------------------------------------
# TRAIN ML MODEL
# ---------------------------------------------------------

training_transactions = []
training_labels = []

for item in training_data:

    transaction = TransactionRequest(
        **item["transaction"]
    )

    training_transactions.append(
        transaction
    )

    training_labels.append(
        item["label"]
    )


train_ml_model(
    training_transactions,
    training_labels
)


# ---------------------------------------------------------
# EVALUATE RULE + ML + HYBRID
# ---------------------------------------------------------

y_true = []

rule_predictions = []
ml_predictions = []
hybrid_predictions = []

transaction_amounts = []


print(
    "\nSentinelPay Model Comparison"
)
print(
    "=" * 70
)


for item in heldout_data:

    transaction = TransactionRequest(
        **item["transaction"]
    )

    actual_label = item["label"]

    # -----------------------------
    # Deterministic SentinelPay
    # -----------------------------

    risk_result = calculate_risk(
        transaction
    )

    behavior_result = analyze_behavior(
        transaction
    )

    graph_result = analyze_graph_risk(
        transaction,
        update_state=False
    )

    merchant_result = (
        analyze_merchant_context(
            transaction
        )
    )

    fusion_result = fuse_risk_scores(
        risk_result,
        behavior_result,
        graph_result,
        merchant_result
    )

    rule_action = fusion_result[
        "final_decision"
    ]

    rule_label = (
        0
        if rule_action == "ALLOW"
        else 1
    )

    # -----------------------------
    # ML prediction
    # -----------------------------

    ml_result = predict_ml_label(
        transaction
    )

    ml_probability = ml_result[
        "ml_fraud_probability"
    ]

    ml_label = ml_result[
        "ml_predicted_label"
    ]

    # -----------------------------
    # Hybrid prediction
    # -----------------------------

    hybrid_result = calculate_hybrid_risk(
        fusion_result[
            "fused_risk_score"
        ],
        ml_probability
    )

    hybrid_action = hybrid_result[
        "hybrid_action"
    ]

    hybrid_label = (
        0
        if hybrid_action == "ALLOW"
        else 1
    )

    # -----------------------------
    # Store results
    # -----------------------------

    y_true.append(
        actual_label
    )

    rule_predictions.append(
        rule_label
    )

    ml_predictions.append(
        ml_label
    )

    hybrid_predictions.append(
        hybrid_label
    )

    transaction_amounts.append(
        transaction.amount
    )

    # -----------------------------
    # Print transaction comparison
    # -----------------------------

    print(
        f"\nTransaction: "
        f"{transaction.transaction_id}"
    )

    print(
        f"Actual: {actual_label}"
    )

    print(
        f"Rule score: "
        f"{fusion_result['fused_risk_score']}"
    )

    print(
        f"Rule prediction: "
        f"{rule_label}"
    )

    print(
        f"ML probability: "
        f"{ml_probability}"
    )

    print(
        f"ML prediction: "
        f"{ml_label}"
    )

    print(
        f"Hybrid score: "
        f"{hybrid_result['hybrid_risk_score']}"
    )

    print(
        f"Hybrid prediction: "
        f"{hybrid_label}"
    )


# ---------------------------------------------------------
# METRICS
# ---------------------------------------------------------

rule_metrics = evaluate_predictions(
    y_true=y_true,
    y_pred=rule_predictions,
    transaction_amounts=transaction_amounts
)

ml_metrics = evaluate_predictions(
    y_true=y_true,
    y_pred=ml_predictions,
    transaction_amounts=transaction_amounts
)

hybrid_metrics = evaluate_predictions(
    y_true=y_true,
    y_pred=hybrid_predictions,
    transaction_amounts=transaction_amounts
)


print(
    "\n" + "=" * 70
)

print(
    "RULE-ONLY METRICS"
)

print(
    "=" * 70
)

for key, value in rule_metrics.items():
    print(
        f"{key}: {value}"
    )


print(
    "\n" + "=" * 70
)

print(
    "ML-ONLY METRICS"
)

print(
    "=" * 70
)

for key, value in ml_metrics.items():
    print(
        f"{key}: {value}"
    )


print(
    "\n" + "=" * 70
)

print(
    "HYBRID METRICS"
)

print(
    "=" * 70
)

for key, value in hybrid_metrics.items():
    print(
        f"{key}: {value}"
    )