from app.razorpay_adapter import (
    razorpay_payment_to_transaction
)


def test_razorpay_payment_adapter():
    payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_001",
                    "amount": 1000,
                    "currency": "INR",
                    "method": "netbanking",
                    "email": "test@example.com",
                    "contact": "9999999999",
                    "created_at": 1788500000
                }
            }
        }
    }

    transaction = razorpay_payment_to_transaction(
        payload
    )

    assert transaction["transaction_id"] == (
        "pay_test_001"
    )

    assert transaction["amount"] == 10.0
    assert transaction["currency"] == "INR"

    assert transaction["payment_method"] == (
        "netbanking"
    )

    assert transaction["email_hash"] != (
        "test@example.com"
    )