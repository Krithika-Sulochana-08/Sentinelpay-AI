import json

from app.schemas import TransactionRequest
from app.ml_engine import (
    train_ml_model,
    predict_ml_label,
    save_ml_model
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


training_result = train_ml_model(
    training_transactions,
    training_labels
)

save_result = save_ml_model()

print(
    f"Model persistence: "
    f"{save_result}"
)

print(
    "\nSentinelPay ML Training"
)
print(
    "=" * 60
)

for key, value in training_result.items():
    print(
        f"{key}: {value}"
    )


y_true = []
y_pred_ml = []
transaction_amounts = []


print(
    "\nSentinelPay ML Held-Out Predictions"
)
print(
    "=" * 60
)


for item in heldout_data:

    transaction = TransactionRequest(
        **item["transaction"]
    )

    actual_label = item[
        "label"
    ]

    ml_result = predict_ml_label(
        transaction
    )

    y_true.append(
        actual_label
    )

    y_pred_ml.append(
        ml_result[
            "ml_predicted_label"
        ]
    )

    transaction_amounts.append(
        transaction.amount
    )

    print(
        f"\nTransaction: "
        f"{transaction.transaction_id}"
    )

    print(
        f"Actual label: "
        f"{actual_label}"
    )

    print(
        f"ML probability: "
        f"{ml_result['ml_fraud_probability']}"
    )

    print(
        f"ML prediction: "
        f"{ml_result['ml_predicted_label']}"
    )


ml_metrics = evaluate_predictions(
    y_true=y_true,
    y_pred=y_pred_ml,
    transaction_amounts=transaction_amounts
)


print(
    "\n" + "=" * 60
)

print(
    "ML-Only Held-Out Metrics"
)

print(
    "=" * 60
)


for key, value in ml_metrics.items():
    print(
        f"{key}: {value}"
    )