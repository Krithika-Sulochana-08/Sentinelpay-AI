from app.evaluation_engine import evaluate_predictions


# Held-out ground-truth labels
# 1 = FRAUD
# 0 = LEGITIMATE
y_true = [
    1, 0, 1, 0, 1,
    0, 0, 1, 1, 0
]


# SentinelPay predicted labels
# 1 = FRAUD / intervention required
# 0 = LEGITIMATE / allow
y_pred = [
    1, 0, 1, 0, 1,
    1, 0, 0, 1, 0
]


transaction_amounts = [
    12000,
    1500,
    22000,
    800,
    50000,
    2000,
    700,
    18000,
    30000,
    1200
]


results = evaluate_predictions(
    y_true=y_true,
    y_pred=y_pred,
    transaction_amounts=transaction_amounts
)


print("\nSentinelPay Held-Out Evaluation")
print("-" * 40)

for key, value in results.items():
    print(f"{key}: {value}")