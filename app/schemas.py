from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TransactionRequest(BaseModel):
    # Core transaction identity
    transaction_id: str
    merchant_id: str
    customer_id: str

    # Payment information
    amount: float = Field(gt=0)
    currency: str = "INR"
    payment_method: str

    # Transaction context
    timestamp: datetime
    country: str
    city: Optional[str] = None

    # Device / network signals
    device_id: str
    ip_address: str
    is_new_device: bool = False

    # Behavioural signals
    account_age_days: int = Field(ge=0)
    transactions_last_1h: int = Field(ge=0)
    transactions_last_24h: int = Field(ge=0)
    avg_transaction_amount_30d: float = Field(ge=0)

    # Relationship signals for later graph intelligence
    card_fingerprint: Optional[str] = None
    email_hash: Optional[str] = None