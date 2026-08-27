def calculate_risk(transaction):
    score = 0
    reasons = []

    # 1. Amount anomaly
    avg_amount = transaction.avg_transaction_amount_30d

    if avg_amount > 0:
        amount_ratio = transaction.amount / avg_amount

        if amount_ratio >= 5:
            score += 30
            reasons.append(
                "Transaction amount is at least 5x the customer's 30-day average"
            )
        elif amount_ratio >= 3:
            score += 20
            reasons.append(
                "Transaction amount is at least 3x the customer's 30-day average"
            )
        elif amount_ratio >= 2:
            score += 10
            reasons.append(
                "Transaction amount is at least 2x the customer's 30-day average"
            )

    # 2. New device risk
    if transaction.is_new_device:
        score += 15
        reasons.append("Transaction originated from a new device")

    # 3. Account age risk
    if transaction.account_age_days < 7:
        score += 20
        reasons.append("Customer account is less than 7 days old")
    elif transaction.account_age_days < 30:
        score += 10
        reasons.append("Customer account is less than 30 days old")

    # 4. High transaction velocity
    if transaction.transactions_last_1h >= 10:
        score += 25
        reasons.append("Very high transaction velocity in the last hour")
    elif transaction.transactions_last_1h >= 5:
        score += 15
        reasons.append("High transaction velocity in the last hour")

    # 5. High daily transaction activity
    if transaction.transactions_last_24h >= 30:
        score += 15
        reasons.append("Unusually high transaction activity in the last 24 hours")
    elif transaction.transactions_last_24h >= 15:
        score += 8
        reasons.append("Elevated transaction activity in the last 24 hours")

    # Cap score at 100
    score = min(score, 100)

    # Convert score into risk level and decision
    if score >= 70:
        risk_level = "HIGH"
        decision = "REVIEW"
    elif score >= 35:
        risk_level = "MEDIUM"
        decision = "VERIFY"
    else:
        risk_level = "LOW"
        decision = "ALLOW"

    # If nothing suspicious was found
    if not reasons:
        reasons.append("No major risk indicators detected")

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "decision": decision,
        "reasons": reasons
    }