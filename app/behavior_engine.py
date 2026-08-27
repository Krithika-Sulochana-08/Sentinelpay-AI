def analyze_behavior(transaction):
    """
    Analyze how unusual the current transaction is
    compared with the customer's recent behaviour.
    """

    signals = []
    anomaly_score = 0

    average_amount = transaction.avg_transaction_amount_30d

    # Amount deviation
    if average_amount > 0:
        amount_ratio = transaction.amount / average_amount
    else:
        amount_ratio = 1

    if amount_ratio >= 10:
        anomaly_score += 40
        signals.append(
            "Transaction amount is more than 10x the customer's 30-day average"
        )

    elif amount_ratio >= 5:
        anomaly_score += 25
        signals.append(
            "Transaction amount is more than 5x the customer's 30-day average"
        )

    elif amount_ratio >= 3:
        anomaly_score += 15
        signals.append(
            "Transaction amount is significantly above the customer's normal spending"
        )

    # Transaction velocity
    if transaction.transactions_last_1h >= 5:
        anomaly_score += 25
        signals.append(
            "Unusual transaction frequency detected in the last hour"
        )

    # New device behaviour
    if transaction.is_new_device:
        anomaly_score += 15
        signals.append(
            "Transaction originated from a new device"
        )

    # Very new account
    if transaction.account_age_days < 7:
        anomaly_score += 20
        signals.append(
            "Transaction originated from a recently created account"
        )

    anomaly_score = min(anomaly_score, 100)

    if anomaly_score >= 70:
        behavior_status = "HIGHLY_ANOMALOUS"
    elif anomaly_score >= 40:
        behavior_status = "ANOMALOUS"
    elif anomaly_score >= 20:
        behavior_status = "SLIGHTLY_UNUSUAL"
    else:
        behavior_status = "NORMAL"

    return {
        "behavior_anomaly_score": anomaly_score,
        "behavior_status": behavior_status,
        "amount_deviation_ratio": round(amount_ratio, 2),
        "behavior_signals": signals
    }