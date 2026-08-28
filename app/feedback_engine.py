from datetime import datetime


# In-memory feedback store for hackathon prototype
# Later this can be replaced with PostgreSQL / Redis / a data warehouse.
review_feedback = []


VALID_OUTCOMES = {
    "FRAUD",
    "LEGITIMATE"
}


def record_review_feedback(
    transaction_id,
    review_outcome,
    reviewer_note=None
):
    """
    Store human-review feedback for a transaction.

    This does not automatically retrain models or
    modify production thresholds.
    """

    normalized_outcome = review_outcome.upper().strip()

    if normalized_outcome not in VALID_OUTCOMES:
        raise ValueError(
            "review_outcome must be FRAUD or LEGITIMATE"
        )

    feedback_entry = {
        "transaction_id": transaction_id,
        "review_outcome": normalized_outcome,
        "reviewer_note": reviewer_note,
        "recorded_at": datetime.utcnow().isoformat()
    }

    review_feedback.append(
        feedback_entry
    )

    return feedback_entry


def get_feedback_summary():
    """
    Return aggregate reviewer feedback statistics.
    """

    total_reviews = len(review_feedback)

    fraud_count = sum(
        1
        for item in review_feedback
        if item["review_outcome"] == "FRAUD"
    )

    legitimate_count = sum(
        1
        for item in review_feedback
        if item["review_outcome"] == "LEGITIMATE"
    )

    if total_reviews > 0:
        fraud_confirmation_rate = round(
            fraud_count / total_reviews,
            3
        )

        legitimate_rate = round(
            legitimate_count / total_reviews,
            3
        )

    else:
        fraud_confirmation_rate = 0.0
        legitimate_rate = 0.0

    return {
        "total_reviews": total_reviews,
        "confirmed_fraud": fraud_count,
        "confirmed_legitimate": legitimate_count,
        "fraud_confirmation_rate": fraud_confirmation_rate,
        "legitimate_rate": legitimate_rate
    }


def get_recent_feedback(limit=10):
    """
    Return the most recent reviewer feedback.
    """

    return review_feedback[-limit:]