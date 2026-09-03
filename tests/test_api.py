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

def test_ml_cannot_override_authoritative_policy(monkeypatch):
    """
    Safety invariant:
    ML is advisory only. Even if ML predicts legitimate,
    deterministic policy must retain the authoritative action.
    """

    def fake_ml_prediction(transaction):
        return {
            "ml_fraud_probability": 0.01,
            "ml_predicted_label": 0,
            "ml_threshold": 0.5
        }

    monkeypatch.setattr(
        "app.main.predict_ml_label",
        fake_ml_prediction
    )

    payload = {
        "transaction_id": "txn_safety_ml_001",
        "merchant_id": "merchant_safety",
        "customer_id": "customer_safety",
        "amount": 50000,
        "currency": "INR",
        "payment_method": "card",
        "timestamp": "2026-09-03T20:00:00",
        "country": "IN",
        "city": "Chennai",
        "device_id": "device_safety_001",
        "ip_address": "10.10.10.10",
        "is_new_device": True,
        "account_age_days": 2,
        "transactions_last_1h": 10,
        "transactions_last_24h": 20,
        "avg_transaction_amount_30d": 2000,
        "card_fingerprint": "card_safety_001",
        "email_hash": "email_safety_001"
    }

    response = client.post("/risk/analyze", json=payload)

    assert response.status_code == 200

    data = response.json()

    # Forced ML opinion says legitimate
    assert data["ml_predicted_label"] == 0
    assert data["ml_fraud_probability"] == 0.01

    # But ML must not override the policy gate
    assert data["authoritative_action"] == "REVIEW"
    assert data["risk_level"] == "HIGH"


def test_sensitive_identifiers_not_exposed_in_response():
    """
    Safety invariant:
    Raw sensitive identifiers must not be returned
    by the risk-analysis API.
    """

    sensitive_device = "secret-device-12345"
    sensitive_ip = "192.168.99.123"
    sensitive_card = "secret-card-fingerprint-98765"
    sensitive_email = "secret-email-hash-54321"

    payload = {
        "transaction_id": "txn_privacy_safety_001",
        "merchant_id": "merchant_privacy",
        "customer_id": "customer_privacy",
        "amount": 12000,
        "currency": "INR",
        "payment_method": "card",
        "timestamp": "2026-09-03T20:30:00",
        "country": "IN",
        "city": "Chennai",
        "device_id": sensitive_device,
        "ip_address": sensitive_ip,
        "is_new_device": False,
        "account_age_days": 500,
        "transactions_last_1h": 1,
        "transactions_last_24h": 2,
        "avg_transaction_amount_30d": 11000,
        "card_fingerprint": sensitive_card,
        "email_hash": sensitive_email
    }

    response = client.post("/risk/analyze", json=payload)

    assert response.status_code == 200

    response_text = response.text

    assert sensitive_device not in response_text
    assert sensitive_ip not in response_text
    assert sensitive_card not in response_text
    assert sensitive_email not in response_text

    data = response.json()

    assert data["privacy_controls"]["raw_card_number_stored"] is False
    assert data["privacy_controls"]["raw_sensitive_identifiers_logged"] is False

def test_invalid_human_review_outcome_rejected():
    """
    Safety invariant:
    Human-review outcomes must be restricted to the
    explicitly permitted FRAUD or LEGITIMATE states.
    """

    payload = {
        "transaction_id": "txn_invalid_review_001",
        "review_outcome": "UNKNOWN",
        "reviewer_note": "Invalid outcome safety test"
    }

    response = client.post("/feedback/review", json=payload)
    assert response.status_code == 422