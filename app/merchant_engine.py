# Prototype merchant profiles.
# In production, these values would be learned from historical
# merchant transaction data or retrieved from a persistent store.

merchant_profiles = {
    "merchant_electronics_01": {
        "category": "electronics",
        "typical_amount": 12000,
        "high_amount_threshold": 50000
    },

    "merchant_food_01": {
        "category": "food",
        "typical_amount": 500,
        "high_amount_threshold": 3000
    },

    "merchant_fashion_01": {
        "category": "fashion",
        "typical_amount": 2500,
        "high_amount_threshold": 15000
    }
}


def analyze_merchant_context(transaction):
    """
    Evaluate whether the transaction amount is unusual
    for the merchant receiving the payment.
    """

    profile = merchant_profiles.get(transaction.merchant_id)

    # Unknown merchant
    if profile is None:
        return {
            "merchant_context_score": 0,
            "merchant_context_status": "UNKNOWN_MERCHANT",
            "merchant_category": "unknown",
            "merchant_amount_ratio": None,
            "merchant_signals": []
        }

    typical_amount = profile["typical_amount"]
    high_threshold = profile["high_amount_threshold"]

    amount_ratio = transaction.amount / typical_amount

    score = 0
    signals = []

    if transaction.amount >= high_threshold:
        score += 50
        signals.append(
            "Transaction exceeds the merchant's high-value threshold"
        )

    elif amount_ratio >= 5:
        score += 35
        signals.append(
            "Transaction is more than 5x the merchant's typical amount"
        )

    elif amount_ratio >= 3:
        score += 20
        signals.append(
            "Transaction is significantly above the merchant's typical amount"
        )

    score = min(score, 100)

    if score >= 50:
        status = "HIGH_MERCHANT_ANOMALY"
    elif score >= 20:
        status = "MERCHANT_ANOMALY"
    else:
        status = "NORMAL_FOR_MERCHANT"

    return {
        "merchant_context_score": score,
        "merchant_context_status": status,
        "merchant_category": profile["category"],
        "merchant_amount_ratio": round(amount_ratio, 2),
        "merchant_signals": signals
    }