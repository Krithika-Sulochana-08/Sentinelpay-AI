from fastapi import FastAPI
from app.schemas import TransactionRequest
from app.risk_engine import calculate_risk
from app.behavior_engine import analyze_behavior
from app.fusion_engine import fuse_risk_scores
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
    behavior_result = analyze_behavior(transaction)
    fusion_result = fuse_risk_scores(
    risk_result,
    behavior_result
)
    return {
        "transaction_id": transaction.transaction_id,
        "merchant_id": transaction.merchant_id,
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "decision": risk_result["decision"],
        "reasons": risk_result["reasons"],
        "behavior_anomaly_score": behavior_result["behavior_anomaly_score"],
        "behavior_status": behavior_result["behavior_status"],
        "amount_deviation_ratio": behavior_result["amount_deviation_ratio"],
        "behavior_signals": behavior_result["behavior_signals"],
        "fused_risk_score": fusion_result["fused_risk_score"],
        "final_risk_level": fusion_result["final_risk_level"],
        "final_decision": fusion_result["final_decision"],
        "fusion_components": fusion_result["fusion_components"],
    }