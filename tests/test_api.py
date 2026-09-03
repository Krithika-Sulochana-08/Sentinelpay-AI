from fastapi.testclient import TestClient

from app.main import app


from app.ml_engine import load_ml_model

load_ml_model()

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200


def test_low_risk_transaction():
    payload = {
        "transaction_id": "test_low_001",
        "merchant_id": "merchant_electronics_01",
        "customer_id": "customer_test_low_001",
        "amount": 12000,
        "currency": "INR",
        "payment_method": "card",
        "timestamp": "2026-09-03T12:30:00",
        "country": "IN",
        "city": "Chennai",
        "device_id": "test_device_low_001",
        "ip_address": "10.50.0.1",
        "is_new_device": False,
        "account_age_days": 500,
        "transactions_last_1h": 1,
        "transactions_last_24h": 2,
        "avg_transaction_amount_30d": 11000,
        "card_fingerprint": "test_card_low_001",
        "email_hash": "test_email_low_001"
    }

    response = client.post(
        "/risk/analyze",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_level"] == "LOW"
    assert data["authoritative_action"] == "ALLOW"

    # Verify ML advisory output
    assert "ml_fraud_probability" in data
    assert data["ml_predicted_label"] == 0

    # Verify privacy controls
    assert "privacy_controls" in data
    assert (
        data["privacy_controls"][
            "raw_sensitive_identifiers_logged"
        ]
        is False
    )

    # Verify renamed evidence field
    assert "risk_evidence_strength" in data
    assert "explanation_confidence" not in data

def test_high_risk_transaction():
    payload = {
        "transaction_id": "test_high_001",
        "merchant_id": "merchant_electronics_01",
        "customer_id": "customer_test_high_001",
        "amount": 50000,
        "currency": "INR",
        "payment_method": "card",
        "timestamp": "2026-09-03T12:35:00",
        "country": "IN",
        "city": "Chennai",
        "device_id": "test_device_high_001",
        "ip_address": "10.60.0.1",
        "is_new_device": True,
        "account_age_days": 2,
        "transactions_last_1h": 10,
        "transactions_last_24h": 20,
        "avg_transaction_amount_30d": 2000,
        "card_fingerprint": "test_card_high_001",
        "email_hash": "test_email_high_001"
    }

    response = client.post(
        "/risk/analyze",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_level"] == "HIGH"
    assert data["authoritative_action"] == "REVIEW"

    # ML advisory should identify elevated fraud risk
    assert data["ml_predicted_label"] == 1
    assert data["ml_fraud_probability"] > 0.8

    # Strong suspicious evidence should be present
    assert len(data["top_evidence"]) > 0
    assert data["risk_evidence_strength"] in [
        "MEDIUM",
        "HIGH"
    ]

    # High-risk cases should trigger human review guidance
    assert data["human_review_recommended"] is True


def test_invalid_negative_amount_returns_422():
    payload = {
        "transaction_id": "test_invalid_001",
        "merchant_id": "merchant_electronics_01",
        "customer_id": "customer_invalid_001",
        "amount": -500,
        "currency": "INR",
        "payment_method": "card",
        "timestamp": "2026-09-03T12:40:00",
        "country": "IN",
        "city": "Chennai",
        "device_id": "test_device_invalid_001",
        "ip_address": "10.70.0.1",
        "is_new_device": False,
        "account_age_days": 100,
        "transactions_last_1h": 1,
        "transactions_last_24h": 2,
        "avg_transaction_amount_30d": 1000,
        "card_fingerprint": "test_card_invalid_001",
        "email_hash": "test_email_invalid_001"
    }

    response = client.post(
        "/risk/analyze",
        json=payload
    )

    assert response.status_code == 422