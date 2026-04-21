"""
Decision Gate - Determines if we should answer or refuse.

This is a critical safety mechanism.

Philosophy: When in doubt, refuse.
Better to refuse a good query than hallucinate a bad answer.

Decision criteria:
1. Confidence score (primary)
2. Risk assessment (secondary)
3. Citation validation (blocker)
4. Counter-argument severity (modifier)
"""

from loguru import logger
from ..schemas.state import GraphState
from ..utils.config import get_settings


def decision_gate_node(state: GraphState) -> GraphState:
    """
    Decide whether to answer or refuse based on confidence and risk.
    
    Decision logic (strict):
    1. If any citation invalid → REFUSE (hard blocker)
    2. If confidence < low_threshold → REFUSE
    3. If confidence < high_threshold → ANSWER with warnings
    4. If risk = critical → REFUSE (even with high confidence)
    5. If confidence >= high_threshold AND risk < critical → ANSWER
    
    Why this ordering:
    - Citation validation first (integrity)
    - Then confidence (certainty)
    - Then risk (safety)
    
    Trade-offs:
    - Conservative thresholds → More refusals but fewer errors
    - Aggressive thresholds → More answers but more risk
    - We err on conservative (legal liability > user satisfaction)
    
    Production tuning:
    - Monitor refusal rate by category
    - Adjust thresholds based on error rate
    - A/B test different thresholds
    """
    settings = get_settings()
    query_id = state.get("query_id", "unknown")
    
    # Extract scoring results
    confidence = state.get("confidence")
    risk = state.get("risk")
    verification = state.get("verification_result")
    counter_args = state.get("counter_arguments")
    
    # Safety check: ensure we have all required data
    if not confidence or not risk or not verification:
        logger.error(f"Decision gate missing required data: {query_id}")
        return {
            **state,
            "should_answer": False,
            "error": "Missing confidence, risk, or verification data"
        }
    
    # RULE 1: Citation validation is a hard blocker
    if not verification.all_citations_valid:
        logger.warning(
            f"Decision gate REFUSE: Invalid citations ({query_id})",
            extra={
                "query_id": query_id,
                "invalid_count": verification.invalid_citations,
            }
        )
        return {
            **state,
            "should_answer": False,
        }
    
    # RULE 2: Critical risk - be transparent but cautious
    # Changed: Show answer with heavy warnings instead of hard refusal
    # Rationale: User can see the analysis and make informed decision
    if risk.overall_risk == "critical":
        # If confidence is very low, still refuse
        if confidence.overall_score < settings.low_confidence_threshold:
            logger.warning(
                f"Decision gate REFUSE: Critical risk + low confidence ({query_id})",
                extra={
                    "query_id": query_id,
                    "confidence": confidence.overall_score,
                    "risk_factors": risk.risk_factors,
                }
            )
            return {
                **state,
                "should_answer": False,
            }
        # If confidence is decent, answer with heavy warnings
        else:
            logger.warning(
                f"Decision gate ANSWER WITH WARNINGS: Critical risk but acceptable confidence ({query_id})",
                extra={
                    "query_id": query_id,
                    "confidence": confidence.overall_score,
                    "risk_factors": risk.risk_factors,
                }
            )
            # Continue to other checks (don't return early)
            # This allows the answer to show with risk badge and warnings
    
    # RULE 3: Low confidence → refuse
    if confidence.overall_score < settings.low_confidence_threshold:
        logger.warning(
            f"Decision gate REFUSE: Low confidence ({query_id})",
            extra={
                "query_id": query_id,
                "confidence": confidence.overall_score,
                "threshold": settings.low_confidence_threshold,
            }
        )
        return {
            **state,
            "should_answer": False,
        }
    
    # RULE 4: Severe counter-arguments + medium confidence → refuse
    # (Even if above threshold, severe counter-arguments indicate high uncertainty)
    if counter_args and counter_args.severity == "severe":
        if confidence.overall_score < settings.high_confidence_threshold:
            logger.warning(
                f"Decision gate REFUSE: Severe counter-arguments + medium confidence ({query_id})",
                extra={
                    "query_id": query_id,
                    "confidence": confidence.overall_score,
                    "counter_severity": counter_args.severity,
                }
            )
            return {
                **state,
                "should_answer": False,
            }
    
    # RULE 5: All checks passed → answer
    logger.info(
        f"Decision gate ANSWER ({query_id})",
        extra={
            "query_id": query_id,
            "confidence": confidence.overall_score,
            "risk": risk.overall_risk,
        }
    )
    
    return {
        **state,
        "should_answer": True,
    }

