from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import os
import joblib

MODEL_PATH = "models/sentinelpay_logreg.joblib"

FEATURE_NAMES = [
    "amount_deviation_ratio",
    "is_new_device",
    "account_age_days",
    "transactions_last_1h",
    "transactions_last_24h",
]


ml_model = Pipeline(
    steps=[
        (
            "scaler",
            StandardScaler()
        ),
        (
            "classifier",
            LogisticRegression(
                random_state=42,
                max_iter=1000,
                class_weight="balanced"
            )
        )
    ]
)


model_trained = False


def extract_ml_features(transaction):
    """
    Convert a SentinelPay transaction into numerical
    features suitable for the ML fraud classifier.
    """

    if transaction.avg_transaction_amount_30d > 0:
        amount_deviation_ratio = (
            transaction.amount
            / transaction.avg_transaction_amount_30d
        )
    else:
        amount_deviation_ratio = 0.0

    return [
        float(amount_deviation_ratio),
        int(transaction.is_new_device),
        int(transaction.account_age_days),
        int(transaction.transactions_last_1h),
        int(transaction.transactions_last_24h),
    ]


def train_ml_model(
    transactions,
    labels
):
    """
    Train the SentinelPay ML fraud classifier.

    labels:
        1 = FRAUD
        0 = LEGITIMATE
    """

    global model_trained

    if len(transactions) != len(labels):
        raise ValueError(
            "Transaction count and label count must match"
        )

    if len(set(labels)) < 2:
        raise ValueError(
            "Training data must contain both FRAUD "
            "and LEGITIMATE samples"
        )

    features = [
        extract_ml_features(transaction)
        for transaction in transactions
    ]

    ml_model.fit(
        features,
        labels
    )

    model_trained = True

    return {
        "model": "LogisticRegression",
        "training_samples": len(transactions),
        "features": FEATURE_NAMES,
        "status": "TRAINED"
    }


def predict_fraud_probability(
    transaction
):
    """
    Return ML fraud probability for one transaction.
    """

    if not model_trained:
        raise RuntimeError(
            "ML model has not been trained"
        )

    features = extract_ml_features(
        transaction
    )

    probability = ml_model.predict_proba(
        [features]
    )[0][1]

    return round(
        float(probability),
        4
    )


def predict_ml_label(
    transaction,
    threshold=0.5
):
    """
    Convert ML fraud probability into a binary label.
    """

    probability = predict_fraud_probability(
        transaction
    )

    predicted_label = (
        1
        if probability >= threshold
        else 0
    )

    return {
        "ml_fraud_probability": probability,
        "ml_predicted_label": predicted_label,
        "ml_threshold": threshold
    }

def save_ml_model(
    model_path=MODEL_PATH
):
    """
    Persist the trained ML pipeline to disk.
    """

    if not model_trained:
        raise RuntimeError(
            "ML model has not been trained"
        )

    os.makedirs(
        os.path.dirname(model_path),
        exist_ok=True
    )

    joblib.dump(
        ml_model,
        model_path
    )

    return {
        "status": "SAVED",
        "model_path": model_path
    }


def load_ml_model(
    model_path=MODEL_PATH
):
    """
    Load a previously trained ML pipeline from disk.
    """

    global ml_model
    global model_trained

    if not os.path.exists(
        model_path
    ):
        return {
            "status": "NOT_FOUND",
            "model_path": model_path
        }

    ml_model = joblib.load(
        model_path
    )

    model_trained = True

    return {
        "status": "LOADED",
        "model_path": model_path
    }