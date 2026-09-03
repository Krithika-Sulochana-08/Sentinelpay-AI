from app.schemas import TransactionRequest
from app.privacy_engine import (
    protect_sensitive_identifiers,
    get_privacy_metadata
)


transaction = TransactionRequest(
    transaction_id="txn_privacy_001",
    merchant_id="merchant_electronics_01",
    customer_id="cust_privacy_001",
    amount=12000,
    currency="INR",
    payment_method="card",
    timestamp="2026-08-31T20:55:00",
    country="IN",
    city="Chennai",
    device_id="device-secret-001",
    ip_address="192.168.10.25",
    is_new_device=False,
    account_age_days=500,
    transactions_last_1h=1,
    transactions_last_24h=2,
    avg_transaction_amount_30d=11000,
    card_fingerprint="card-secret-001",
    email_hash="email-secret-001"
)


protected = protect_sensitive_identifiers(
    transaction
)

metadata = get_privacy_metadata()


print("\nProtected identifiers")
print("=" * 60)

for key, value in protected.items():
    print(f"{key}: {value}")


print("\nPrivacy metadata")
print("=" * 60)

for key, value in metadata.items():
    print(f"{key}: {value}")