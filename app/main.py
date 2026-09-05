from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import json
import os

from app.schemas import (
    TransactionRequest,
    ReviewFeedbackRequest
)

from app.razorpay_engine import (
    verify_webhook_signature,
    is_duplicate_event,
    mark_event_processed
)

from app.razorpay_adapter import (
    razorpay_payment_to_transaction
)

from app.risk_engine import calculate_risk
from app.behavior_engine import analyze_behavior
from app.graph_engine import analyze_graph_risk
from app.merchant_engine import analyze_merchant_context
from app.confidence_engine import analyze_confidence
from app.fusion_engine import fuse_risk_scores
from app.cost_engine import evaluate_decision_costs
from app.policy_engine import resolve_final_action
from app.counterfactual_engine import run_counterfactual_analysis
from app.explainability_engine import generate_explanation
from app.drift_engine import update_drift_monitor
from app.privacy_engine import get_privacy_metadata

from app.feedback_engine import (
    record_review_feedback,
    get_feedback_summary,
    get_recent_feedback
)

from app.ml_engine import (
    load_ml_model,
    predict_ml_label
)


# =========================================================
# ENVIRONMENT CONFIGURATION
# =========================================================

load_dotenv()

RAZORPAY_WEBHOOK_SECRET = os.getenv(
    "RAZORPAY_WEBHOOK_SECRET"
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="SentinelPay AI",
    description=(
        "Explainable AI-powered payment "
        "risk intelligence system"
    ),
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =========================================================
# STARTUP
# =========================================================

@app.on_event("startup")
def load_persisted_ml_model():
    result = load_ml_model()

    print(
        "ML model startup status:",
        result
    )


# =========================================================
# BASIC API ROUTES
# =========================================================

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


# =========================================================
# SENTINELPAY RISK ANALYSIS
# =========================================================

@app.post("/risk/analyze")
def analyze_transaction(
    transaction: TransactionRequest
):

    # -----------------------------------------------------
    # 1. Transaction-level risk analysis
    # -----------------------------------------------------

    risk_result = calculate_risk(
        transaction
    )

    # -----------------------------------------------------
    # 2. Behavioral anomaly analysis
    # -----------------------------------------------------

    behavior_result = analyze_behavior(
        transaction
    )

    # -----------------------------------------------------
    # 3. Graph / relationship risk analysis
    # -----------------------------------------------------

    graph_result = analyze_graph_risk(
        transaction
    )

    # -----------------------------------------------------
    # 4. Merchant-context analysis
    # -----------------------------------------------------

    merchant_result = analyze_merchant_context(
        transaction
    )

    # -----------------------------------------------------
    # 5. ML fraud intelligence
    # -----------------------------------------------------

    ml_result = predict_ml_label(
        transaction
    )

    # -----------------------------------------------------
    # 6. Confidence / uncertainty analysis
    # -----------------------------------------------------

    confidence_result = analyze_confidence(
        risk_result,
        behavior_result,
        graph_result,
        merchant_result
    )

    # -----------------------------------------------------
    # 7. Unified risk fusion
    # -----------------------------------------------------

    fusion_result = fuse_risk_scores(
        risk_result,
        behavior_result,
        graph_result,
        merchant_result
    )

    # -----------------------------------------------------
    # 8. Drift / fraud-spike monitoring
    # -----------------------------------------------------

    drift_result = update_drift_monitor(
        fusion_result[
            "fused_risk_score"
        ]
    )

    # -----------------------------------------------------
    # 9. Cost-aware decision analysis
    # -----------------------------------------------------

    cost_result = evaluate_decision_costs(
        transaction,
        fusion_result[
            "fused_risk_score"
        ]
    )

    # -----------------------------------------------------
    # 10. Unified policy resolution
    # -----------------------------------------------------

    policy_result = resolve_final_action(
        fusion_result,
        cost_result
    )

    # -----------------------------------------------------
    # 11. Counterfactual / what-if analysis
    # -----------------------------------------------------

    counterfactual_result = (
        run_counterfactual_analysis(
            transaction
        )
    )

    # -----------------------------------------------------
    # 12. Explainability
    # -----------------------------------------------------

    explanation_result = generate_explanation(
        transaction,
        risk_result,
        behavior_result,
        graph_result,
        merchant_result,
        fusion_result,
        cost_result,
        policy_result
    )

    # -----------------------------------------------------
    # API RESPONSE
    # -----------------------------------------------------

    return {

        # -------------------------------------------------
        # Transaction identity
        # -------------------------------------------------

        "transaction_id":
            transaction.transaction_id,

        "merchant_id":
            transaction.merchant_id,

        # -------------------------------------------------
        # Transaction risk
        # -------------------------------------------------

        "risk_score":
            risk_result[
                "risk_score"
            ],

        "risk_level":
            risk_result[
                "risk_level"
            ],

        "decision":
            risk_result[
                "decision"
            ],

        "reasons":
            risk_result[
                "reasons"
            ],

        # -------------------------------------------------
        # Behavioral risk
        # -------------------------------------------------

        "behavior_anomaly_score":
            behavior_result[
                "behavior_anomaly_score"
            ],

        "behavior_status":
            behavior_result[
                "behavior_status"
            ],

        "amount_deviation_ratio":
            behavior_result[
                "amount_deviation_ratio"
            ],

        "behavior_signals":
            behavior_result[
                "behavior_signals"
            ],

        # -------------------------------------------------
        # Graph intelligence
        # -------------------------------------------------

        "graph_risk_score":
            graph_result[
                "graph_risk_score"
            ],

        "graph_status":
            graph_result[
                "graph_status"
            ],

        "graph_signals":
            graph_result[
                "graph_signals"
            ],

        "linked_account_counts":
            graph_result[
                "linked_account_counts"
            ],

        # -------------------------------------------------
        # Merchant context
        # -------------------------------------------------

        "merchant_context_score":
            merchant_result[
                "merchant_context_score"
            ],

        "merchant_context_status":
            merchant_result[
                "merchant_context_status"
            ],

        "merchant_category":
            merchant_result[
                "merchant_category"
            ],

        "merchant_amount_ratio":
            merchant_result[
                "merchant_amount_ratio"
            ],

        "merchant_signals":
            merchant_result[
                "merchant_signals"
            ],

        # -------------------------------------------------
        # ML fraud intelligence
        # -------------------------------------------------

        "ml_fraud_probability":
            ml_result[
                "ml_fraud_probability"
            ],

        "ml_predicted_label":
            ml_result[
                "ml_predicted_label"
            ],

        "ml_threshold":
            ml_result[
                "ml_threshold"
            ],

        # -------------------------------------------------
        # Confidence / uncertainty
        # -------------------------------------------------

        "decision_confidence":
            confidence_result[
                "decision_confidence"
            ],

        "uncertainty_score":
            confidence_result[
                "uncertainty_score"
            ],

        "signal_agreement":
            confidence_result[
                "signal_agreement"
            ],

        "human_review_recommended":
            confidence_result[
                "human_review_recommended"
            ],

        "confidence_signal_scores":
            confidence_result[
                "signal_scores"
            ],

        # -------------------------------------------------
        # Unified risk
        # -------------------------------------------------

        "fused_risk_score":
            fusion_result[
                "fused_risk_score"
            ],

        "final_risk_level":
            fusion_result[
                "final_risk_level"
            ],

        "final_decision":
            policy_result[
                "authoritative_action"
            ],

        "fusion_components":
            fusion_result[
                "fusion_components"
            ],

        # -------------------------------------------------
        # Cost-aware decisioning
        # -------------------------------------------------

        "estimated_action_costs":
            cost_result[
                "estimated_action_costs"
            ],

        "cost_optimized_action":
            cost_result[
                "cost_optimized_action"
            ],

        "minimum_expected_cost":
            cost_result[
                "minimum_expected_cost"
            ],

        # -------------------------------------------------
        # Policy resolution
        # -------------------------------------------------

        "risk_recommended_action":
            policy_result[
                "risk_recommended_action"
            ],

        "cost_recommended_action":
            policy_result[
                "cost_recommended_action"
            ],

        "authoritative_action":
            policy_result[
                "authoritative_action"
            ],

        "policy_resolution_reason":
            policy_result[
                "policy_resolution_reason"
            ],

        # -------------------------------------------------
        # Counterfactual analysis
        # -------------------------------------------------

        "counterfactuals_available":
            counterfactual_result[
                "counterfactuals_available"
            ],

        "counterfactual_scenarios":
            counterfactual_result[
                "counterfactual_scenarios"
            ],

        # -------------------------------------------------
        # Explainability
        # -------------------------------------------------

        "decision_summary":
            explanation_result[
                "decision_summary"
            ],

        "recommended_action":
            explanation_result[
                "recommended_action"
            ],

        "top_evidence":
            explanation_result[
                "top_evidence"
            ],

        "risk_evidence_strength":
            explanation_result[
                "risk_evidence_strength"
            ],

        # -------------------------------------------------
        # Drift monitoring
        # -------------------------------------------------

        "drift_status":
            drift_result[
                "drift_status"
            ],

        "recent_average_risk":
            drift_result[
                "recent_average_risk"
            ],

        "high_risk_ratio":
            drift_result[
                "high_risk_ratio"
            ],

        "fraud_spike_detected":
            drift_result[
                "fraud_spike_detected"
            ],

        # -------------------------------------------------
        # Privacy metadata
        # -------------------------------------------------

        "privacy_controls":
            get_privacy_metadata()
    }


# =========================================================
# HUMAN REVIEW FEEDBACK INTELLIGENCE
# =========================================================

@app.post("/feedback/review")
def submit_review_feedback(
    feedback: ReviewFeedbackRequest
):
    """
    Store the confirmed human-review outcome
    for a SentinelPay transaction.
    """

    feedback_entry = record_review_feedback(
        transaction_id=(
            feedback.transaction_id
        ),
        review_outcome=(
            feedback.review_outcome
        ),
        reviewer_note=(
            feedback.reviewer_note
        )
    )

    return {
        "message":
            "Review feedback recorded successfully",

        "feedback":
            feedback_entry
    }


@app.get("/feedback/summary")
def feedback_summary():
    """
    Return aggregate human-review statistics.
    """

    return get_feedback_summary()


@app.get("/feedback/recent")
def recent_feedback():
    """
    Return recent human-review outcomes.
    """

    return {
        "recent_feedback":
            get_recent_feedback()
    }


# =========================================================
# RAZORPAY WEBHOOK
# =========================================================

@app.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request
):
    """
    Receive Razorpay Test Mode payment events,
    verify authenticity, prevent duplicate processing,
    and analyze captured payments using SentinelPay.
    """

    # -----------------------------------------------------
    # Read exact raw request body
    # -----------------------------------------------------

    raw_body = await request.body()

    # -----------------------------------------------------
    # Razorpay signature
    # -----------------------------------------------------

    received_signature = (
        request.headers.get(
            "X-Razorpay-Signature"
        )
    )

    # -----------------------------------------------------
    # Verify webhook authenticity
    # -----------------------------------------------------

    if not verify_webhook_signature(
        raw_body,
        received_signature,
        RAZORPAY_WEBHOOK_SECRET
    ):
        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid Razorpay webhook signature"
            )
        )

    # -----------------------------------------------------
    # Parse webhook JSON
    # -----------------------------------------------------

    try:
        payload = json.loads(
            raw_body
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook JSON"
        )

    # -----------------------------------------------------
    # Razorpay event idempotency
    # -----------------------------------------------------

    event_id = request.headers.get(
        "x-razorpay-event-id"
    )

    if event_id:

        if is_duplicate_event(
            event_id
        ):
            return {
                "status":
                    "duplicate_ignored",

                "event":
                    payload.get(
                        "event"
                    ),

                "event_id":
                    event_id
            }

        mark_event_processed(
            event_id
        )

    # -----------------------------------------------------
    # Analyze only successfully captured payments
    # -----------------------------------------------------

    if (
        payload.get("event")
        == "payment.captured"
    ):

        transaction_data = (
            razorpay_payment_to_transaction(
                payload
            )
        )

        # Real Razorpay captured-payment payloads
        # contain a positive payment amount.
        #
        # Older minimal unit tests contain only:
        # {"event": "payment.captured"}
        #
        # Those should remain accepted without
        # creating an invalid TransactionRequest.

        if (
            transaction_data.get(
                "amount",
                0
            )
            > 0
        ):

            transaction = (
                TransactionRequest(
                    **transaction_data
                )
            )

            risk_analysis = (
                analyze_transaction(
                    transaction
                )
            )

            return {
                "status":
                    "accepted",

                "event":
                    payload.get(
                        "event"
                    ),

                "sentinelpay_analysis":
                    risk_analysis
            }

    # -----------------------------------------------------
    # Other valid Razorpay events
    # -----------------------------------------------------

    return {
        "status":
            "accepted",

        "event":
            payload.get(
                "event"
            )
    }