from fastapi import FastAPI
from app.schemas import TransactionRequest
from app.risk_engine import calculate_risk
app = FastAPI(
    title="SentinelPay AI",
    description="Explainable AI-powered payment risk intelligence system",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "application": "SentinelPay AI",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.post("/risk/analyze")
def analyze_transaction(transaction: TransactionRequest):
    risk_result = calculate_risk(transaction)

    return {
        "transaction_id": transaction.transaction_id,
        "merchant_id": transaction.merchant_id,
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "decision": risk_result["decision"],
        "reasons": risk_result["reasons"]
    }