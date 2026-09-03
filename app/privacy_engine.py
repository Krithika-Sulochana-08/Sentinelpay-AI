import hashlib


SENSITIVE_FIELDS = {
    "device_id",
    "ip_address",
    "card_fingerprint",
    "email_hash"
}


def _hash_value(value):
    """
    Convert a sensitive identifier into a stable
    SHA-256 token.

    None values are preserved.
    """

    if value is None:
        return None

    normalized_value = str(value).strip()

    return hashlib.sha256(
        normalized_value.encode("utf-8")
    ).hexdigest()


def protect_sensitive_identifiers(transaction):
    """
    Produce a privacy-safe representation of
    transaction identifiers for logging/audit use.

    The live transaction object itself is not modified.
    """

    protected = {
        "transaction_id": transaction.transaction_id,
        "merchant_id": transaction.merchant_id,
        "customer_id": transaction.customer_id,

        "device_id_token": _hash_value(
            transaction.device_id
        ),

        "ip_address_token": _hash_value(
            transaction.ip_address
        ),

        "card_fingerprint_token": _hash_value(
            transaction.card_fingerprint
        ),

        "email_hash_token": _hash_value(
            transaction.email_hash
        )
    }

    return protected


def get_privacy_metadata():
    """
    Describe the privacy controls used by SentinelPay.
    """

    return {
        "raw_card_number_stored": False,
        "raw_sensitive_identifiers_logged": False,
        "identifier_protection": "SHA-256 tokenization",
        "protected_fields": sorted(
            SENSITIVE_FIELDS
        ),
        "purpose": (
            "Reduce exposure of sensitive identifiers "
            "in logs and audit outputs."
        )
    }