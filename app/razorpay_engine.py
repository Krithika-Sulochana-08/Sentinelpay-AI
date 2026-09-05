import hashlib
import hmac


def verify_webhook_signature(
    raw_body: bytes,
    received_signature: str,
    webhook_secret: str
) -> bool:
    """
    Verify that a Razorpay webhook was signed using
    our configured webhook secret.

    Razorpay signs the raw request body using HMAC-SHA256.
    """

    if not received_signature or not webhook_secret:
        return False

    expected_signature = hmac.new(
        webhook_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        received_signature
    )
_processed_event_ids = set()


def is_duplicate_event(event_id: str) -> bool:
    return event_id in _processed_event_ids


def mark_event_processed(event_id: str) -> None:
    _processed_event_ids.add(event_id)


def reset_processed_events() -> None:
    _processed_event_ids.clear()