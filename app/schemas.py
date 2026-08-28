from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


class TransactionRequest(BaseModel):
    transaction_id: str
    merchant_id: str
    customer_id: str

    amount: float = Field(gt=0)
    currency: str = "INR"
    payment_method: str

    timestamp: datetime
    country: str
    city: Optional[str] = None

    device_id: str
    ip_address: str
    is_new_device: bool = False

    account_age_days: int = Field(ge=0)
    transactions_last_1h: int = Field(ge=0)
    transactions_last_24h: int = Field(ge=0)
    avg_transaction_amount_30d: float = Field(ge=0)

    card_fingerprint: Optional[str] = None
    email_hash: Optional[str] = None


class ReviewFeedbackRequest(BaseModel):
    transaction_id: str = Field(
        ...,
        min_length=1
    )

    review_outcome: Literal[
        "FRAUD",
        "LEGITIMATE"
    ]

    reviewer_note: Optional[str] = None