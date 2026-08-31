def evaluate_predictions(
    y_true,
    y_pred,
    transaction_amounts=None,
    false_positive_cost_rate=0.05,
    false_negative_loss_rate=1.0
):
    """
    Evaluate SentinelPay predictions on a held-out labeled dataset.

    y_true:
        List containing actual labels:
        1 = FRAUD
        0 = LEGITIMATE

    y_pred:
        List containing predicted labels:
        1 = FRAUD / REVIEW-BLOCK
        0 = LEGITIMATE / ALLOW

    transaction_amounts:
        Optional list of transaction amounts used
        for business-cost estimation.
    """

    if len(y_true) != len(y_pred):
        raise ValueError(
            "y_true and y_pred must have the same length"
        )

    if transaction_amounts is not None:
        if len(transaction_amounts) != len(y_true):
            raise ValueError(
                "transaction_amounts must match label count"
            )

    tp = 0
    tn = 0
    fp = 0
    fn = 0

    false_positive_cost = 0.0
    fraud_loss_cost = 0.0

    for index, (actual, predicted) in enumerate(
        zip(y_true, y_pred)
    ):

        if actual == 1 and predicted == 1:
            tp += 1

        elif actual == 0 and predicted == 0:
            tn += 1

        elif actual == 0 and predicted == 1:
            fp += 1

            if transaction_amounts is not None:
                false_positive_cost += (
                    transaction_amounts[index]
                    * false_positive_cost_rate
                )

        elif actual == 1 and predicted == 0:
            fn += 1

            if transaction_amounts is not None:
                fraud_loss_cost += (
                    transaction_amounts[index]
                    * false_negative_loss_rate
                )

    total = tp + tn + fp + fn

    accuracy = (
        (tp + tn) / total
        if total > 0
        else 0
    )

    precision = (
        tp / (tp + fp)
        if (tp + fp) > 0
        else 0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn) > 0
        else 0
    )

    f1_score = (
        2 * precision * recall
        / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    false_positive_rate = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0
    )

    false_negative_rate = (
        fn / (fn + tp)
        if (fn + tp) > 0
        else 0
    )

    total_business_cost = round(
        false_positive_cost
        + fraud_loss_cost,
        2
    )

    return {
        "total_samples": total,

        "confusion_matrix": {
            "true_positive": tp,
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn
        },

        "accuracy": round(
            accuracy,
            3
        ),

        "precision": round(
            precision,
            3
        ),

        "recall": round(
            recall,
            3
        ),

        "f1_score": round(
            f1_score,
            3
        ),

        "false_positive_rate": round(
            false_positive_rate,
            3
        ),

        "false_negative_rate": round(
            false_negative_rate,
            3
        ),

        "estimated_false_positive_cost":
            round(false_positive_cost, 2),

        "estimated_fraud_loss_cost":
            round(fraud_loss_cost, 2),

        "estimated_total_business_cost":
            total_business_cost
    }