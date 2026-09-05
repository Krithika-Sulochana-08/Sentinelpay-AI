import hashlib
import hmac

from fastapi.testclient import TestClient

from app.main import app
from app.razorpay_engine import (
    verify_webhook_signature,
    reset_processed_events
)

client = TestClient(app)


def test_valid_razorpay_webhook_signature():
    secret = "sentinelpay-test-webhook-secret"
    raw_body = b'{"event":"payment.captured"}'

    signature = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    assert verify_webhook_signature(
        raw_body,
        signature,
        secret
    ) is True


def test_invalid_razorpay_webhook_signature():
    secret = "sentinelpay-test-webhook-secret"
    raw_body = b'{"event":"payment.captured"}'

    assert verify_webhook_signature(
        raw_body,
        "invalid-signature",
        secret
    ) is False


def test_valid_webhook_endpoint(monkeypatch):
    secret = "sentinelpay-endpoint-test-secret"

    monkeypatch.setattr(
        "app.main.RAZORPAY_WEBHOOK_SECRET",
        secret
    )

    raw_body = b'{"event":"payment.captured"}'

    signature = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    response = client.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": signature
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "accepted"
    assert data["event"] == "payment.captured"


def test_invalid_webhook_endpoint_signature(monkeypatch):
    monkeypatch.setattr(
        "app.main.RAZORPAY_WEBHOOK_SECRET",
        "sentinelpay-endpoint-test-secret"
    )

    raw_body = b'{"event":"payment.captured"}'

    response = client.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": "invalid-signature"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid Razorpay webhook signature"
    )


def test_duplicate_webhook_is_ignored(monkeypatch):
    reset_processed_events()

    secret = "sentinelpay-idempotency-test-secret"

    monkeypatch.setattr(
        "app.main.RAZORPAY_WEBHOOK_SECRET",
        secret
    )

    raw_body = b'{"event":"payment.captured"}'

    signature = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature,
        "x-razorpay-event-id": "evt_test_duplicate_001"
    }

    first_response = client.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers=headers
    )

    second_response = client.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers=headers
    )

    assert first_response.status_code == 200
    assert first_response.json()["status"] == "accepted"

    assert second_response.status_code == 200
    assert (
        second_response.json()["status"]
        == "duplicate_ignored"
    )