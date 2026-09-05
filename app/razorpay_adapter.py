import hashlib
from datetime import datetime, timezone


def _hash_value(value: str) -> str:
    if not value:
        return "unknown"

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def razorpay_payment_to_transaction(payload: dict) -> dict:
    """
    Convert a Razorpay payment webhook into the
    TransactionRequest structure expected by SentinelPay.

    Fields unavailable from Razorpay are given neutral
    prototype defaults so the existing risk pipeline can run.
    """

    payment = (
        payload
        .get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    payment_id = payment.get(
        "id",
        "razorpay_unknown_payment"
    )

    amount_paise = payment.get("amount", 0)

    created_at = payment.get("created_at")

    if created_at:
        timestamp = datetime.fromtimestamp(
            created_at,
            tz=timezone.utc
        ).isoformat()
    else:
        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

    contact = str(payment.get("contact", ""))
    email = str(payment.get("email", ""))

    return {
        "transaction_id": payment_id,

        "merchant_id": "razorpay_test_merchant",

        "customer_id": (
            payment.get("customer_id")
            or "razorpay_test_customer"
        ),

        # Razorpay stores amount in paise
        "amount": amount_paise / 100,

        "currency": payment.get(
            "currency",
            "INR"
        ),

        "payment_method": payment.get(
            "method",
            "unknown"
        ),

        "timestamp": timestamp,

        # Neutral prototype context
        "country": "IN",
        "city": "UNKNOWN",

        "device_id": _hash_value(
            f"device:{payment_id}"
        ),

        "ip_address": "0.0.0.0",

        "is_new_device": False,

        "account_age_days": 365,

        "transactions_last_1h": 1,

        "transactions_last_24h": 1,

        "avg_transaction_amount_30d": (
            amount_paise / 100
        ),

        "card_fingerprint": _hash_value(
            f"payment:{payment_id}"
        ),

        "email_hash": _hash_value(
            email or contact
        )
    }