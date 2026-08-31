def calculate_hybrid_risk(
    fused_risk_score,
    ml_fraud_probability
):
    """
    Decision-level hybrid policy.

    Goal:
    - preserve strong deterministic fraud evidence
    - use strong ML evidence to surface subtle fraud
    - route disagreement to human verification
    - avoid arbitrary weighted score suppression
    """

    ml_score = round(
        ml_fraud_probability * 100,
        2
    )

    # -----------------------------------------------------
    # Case 1: strong deterministic evidence
    # -----------------------------------------------------
    if fused_risk_score >= 70:
        hybrid_score = max(
            fused_risk_score,
            ml_score
        )

        hybrid_risk_level = "HIGH"
        hybrid_action = "REVIEW"

        resolution = (
            "Strong deterministic fraud evidence "
            "is preserved."
        )

    # -----------------------------------------------------
    # Case 2: strong ML evidence
    # -----------------------------------------------------
    elif ml_fraud_probability >= 0.75:
        hybrid_score = max(
            fused_risk_score,
            60
        )

        hybrid_risk_level = "HIGH"
        hybrid_action = "REVIEW"

        resolution = (
            "Strong ML fraud evidence escalates "
            "the transaction for review."
        )

    # -----------------------------------------------------
    # Case 3: moderate deterministic evidence
    #         + moderate ML evidence
    # -----------------------------------------------------
    elif (
        fused_risk_score >= 40
        and ml_fraud_probability >= 0.40
    ):
        hybrid_score = max(
            fused_risk_score,
            ml_score
        )

        hybrid_risk_level = "MEDIUM"
        hybrid_action = "CHALLENGE"

        resolution = (
            "Deterministic and ML signals jointly "
            "indicate moderate risk."
        )

    # -----------------------------------------------------
    # Case 4: signal disagreement
    # -----------------------------------------------------
    elif (
        fused_risk_score >= 40
        or ml_fraud_probability >= 0.40
    ):
        hybrid_score = max(
            fused_risk_score,
            ml_score
        )

        hybrid_risk_level = "MEDIUM"
        hybrid_action = "CHALLENGE"

        resolution = (
            "Risk signals disagree, so additional "
            "verification is recommended."
        )

    # -----------------------------------------------------
    # Case 5: both systems indicate low risk
    # -----------------------------------------------------
    else:
        hybrid_score = max(
            fused_risk_score,
            ml_score
        )

        hybrid_risk_level = "LOW"
        hybrid_action = "ALLOW"

        resolution = (
            "Deterministic and ML signals both "
            "indicate low risk."
        )

    return {
        "hybrid_risk_score": round(
            hybrid_score,
            2
        ),

        "hybrid_risk_level":
            hybrid_risk_level,

        "hybrid_action":
            hybrid_action,

        "hybrid_resolution":
            resolution,

        "hybrid_components": {
            "deterministic_fused_score":
                fused_risk_score,

            "ml_fraud_probability":
                ml_fraud_probability,

            "ml_risk_score":
                ml_score
        }
    }