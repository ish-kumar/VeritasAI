"""
Response formatters - Convert internal state to user-facing responses.

Design principle: Separation of computation vs presentation.
- Agents compute answers
- Formatters present them to users

Why separate:
1. Agents focus on correctness
2. Formatters focus on UX
3. Easy to change presentation without touching logic
4. Can have multiple formatters (API, CLI, UI)
"""

import time
from typing import Optional
from loguru import logger

from ..schemas.state import GraphState
from ..schemas.response import FinalResponse, RefusalReason
from ..utils.config import get_settings


def format_answer_node(state: GraphState) -> GraphState:
    """
    Format a successful answer for the user.
    
    What we include:
    - The answer (obviously)
    - All citations (for verification)
    - Confidence & risk scores (for transparency)
    - Counter-arguments (for balanced view)
    - Warnings if confidence is medium
    - Suggested next steps
    
    Design decision: Radical transparency.
    Show the user everything so they can make informed decisions.
    """
    settings = get_settings()
    query_id = state.get("query_id", "unknown")
    
    answer = state.get("answer")
    confidence = state.get("confidence")
    risk = state.get("risk")
    verification = state.get("verification_result")
    counter_args = state.get("counter_arguments")
    
    # Build warnings
    warnings = []
    
    # Add confidence-based warnings
    if confidence.overall_score < settings.high_confidence_threshold:
        warnings.append(
            f"Medium confidence ({confidence.overall_score:.1f}/100). "
            "This answer may require additional verification."
        )
    
    # Add risk-based warnings
    if risk.overall_risk in ["high", "medium"]:
        warnings.append(
            f"Risk level: {risk.overall_risk}. Consult with legal counsel before taking action."
        )
    
    # Add counter-argument warnings
    if counter_args and counter_args.severity in ["moderate", "severe"]:
        warnings.append(
            f"Significant counter-arguments identified ({counter_args.severity}). "
            "Review the alternative interpretations carefully."
        )
    
    # Add jurisdiction warnings
    if counter_args and counter_args.jurisdictional_issues:
        warnings.append(
            "Jurisdictional complexities may affect this answer. "
            "Verify applicability in your specific jurisdiction."
        )
    
    # Always add the standard legal disclaimer
    warnings.append(
        "This is not legal advice. Consult a licensed attorney for specific legal guidance."
    )
    
    # Enrich citations with document_id (extract from clause_id)
    if answer and answer.citations:
        for citation in answer.citations:
            # Extract document_id from clause_id if not already set
            # Format is typically: "DOC_ID_SEC_X" or "DOC_ID_SEC.X"
            if not citation.document_id and citation.clause_id:
                # Split by common separators and take first part as document ID
                parts = citation.clause_id.replace('_SEC', '|').replace('_CLAUSE', '|').split('|')
                if parts:
                    citation.document_id = parts[0]
                    logger.debug(f"Extracted document_id '{citation.document_id}' from clause_id '{citation.clause_id}'")
    
    # Build next steps
    next_steps = []
    
    if risk.mitigation_suggestions:
        next_steps.extend(risk.mitigation_suggestions)
    
    if counter_args and counter_args.missing_context:
        next_steps.append(
            "Obtain the following missing information: " + 
            ", ".join(counter_args.missing_context[:2])  # Limit to 2 items
        )
    
    # Create final response
    final_response = FinalResponse(
        success=True,
        answer=answer,
        refusal_reason=None,
        refusal_explanation=None,
        confidence=confidence,
        risk=risk,
        counter_arguments=counter_args,
        verification=verification,
        warnings=warnings,
        next_steps=next_steps,
        query_id=query_id,
        processing_time_ms=None,  # TODO: Track timing
    )
    
    logger.info(f"Formatted successful answer: {query_id}")
    
    return {
        **state,
        "final_response": final_response,
    }


def format_refusal_node(state: GraphState) -> GraphState:
    """
    Format a refusal response for the user.
    
    Refusal philosophy: Be helpful even when refusing.
    - Explain WHY we're refusing
    - Explain WHAT'S missing
    - Explain HOW to get a better answer
    
    This turns refusals from dead-ends into learning opportunities.
    
    Design decision: Different refusal types need different explanations.
    """
    settings = get_settings()
    query_id = state.get("query_id", "unknown")
    
    confidence = state.get("confidence")
    risk = state.get("risk")
    verification = state.get("verification_result")
    counter_args = state.get("counter_arguments")
    
    # Determine refusal reason
    refusal_reason, refusal_explanation = determine_refusal_reason(
        confidence, risk, verification, counter_args, settings
    )
    
    # Build next steps for refusal
    next_steps = []
    
    if refusal_reason == RefusalReason.LOW_CONFIDENCE:
        next_steps.append("Provide more specific details about your situation")
        next_steps.append("Specify the jurisdiction more precisely")
        if counter_args and counter_args.missing_context:
            next_steps.append(f"Obtain: {counter_args.missing_context[0]}")
    
    elif refusal_reason == RefusalReason.CITATION_FAILURE:
        next_steps.append("This may indicate missing or incomplete documents")
        next_steps.append("Verify that all relevant documents have been indexed")
        next_steps.append("Try rephrasing your query")
    
    elif refusal_reason == RefusalReason.HIGH_RISK:
        next_steps.append("Consult with a licensed attorney immediately")
        next_steps.append("This query involves high-risk legal matters")
        if risk and risk.liability_concerns:
            next_steps.append(f"Concern: {risk.liability_concerns[0]}")
    
    elif refusal_reason == RefusalReason.INSUFFICIENT_CONTEXT:
        next_steps.append("Provide additional context about your situation")
        if counter_args and counter_args.missing_context:
            for missing in counter_args.missing_context[:3]:
                next_steps.append(f"Needed: {missing}")
    
    elif refusal_reason == RefusalReason.JURISDICTIONAL_CONFLICT:
        next_steps.append("Clarify which jurisdiction applies")
        next_steps.append("Consult local legal counsel familiar with the specific jurisdiction")
    
    # Always suggest consulting an attorney
    next_steps.append("For legal certainty, consult a licensed attorney in your jurisdiction")
    
    # Create final response
    final_response = FinalResponse(
        success=False,
        answer=None,
        refusal_reason=refusal_reason,
        refusal_explanation=refusal_explanation,
        confidence=confidence or _create_default_confidence(),
        risk=risk or _create_default_risk(),
        counter_arguments=counter_args,
        verification=verification or _create_default_verification(),
        warnings=[
            "Unable to provide a reliable answer to this query",
            "The reasons are explained above in the confidence and risk assessment",
        ],
        next_steps=next_steps,
        query_id=query_id,
        processing_time_ms=None,  # TODO: Track timing
    )
    
    logger.warning(
        f"Formatted refusal: {query_id}",
        extra={
            "refusal_reason": refusal_reason,
            "confidence": confidence.overall_score if confidence else 0,
        }
    )
    
    # Log refusal for analytics
    from ..utils.logger import log_refusal
    log_refusal(
        query_id=query_id,
        reason=refusal_reason,
        confidence=confidence.overall_score if confidence else 0.0
    )
    
    return {
        **state,
        "final_response": final_response,
    }


def determine_refusal_reason(
    confidence, risk, verification, counter_args, settings
) -> tuple[RefusalReason, str]:
    """
    Determine the primary refusal reason and explanation.
    
    Priority order (most critical first):
    1. Citation failure (integrity issue)
    2. Critical risk (safety issue)
    3. Low confidence (uncertainty issue)
    4. Jurisdictional conflict (applicability issue)
    5. Insufficient context (information issue)
    """
    
    # Check citation validation
    if verification and not verification.all_citations_valid:
        return (
            RefusalReason.CITATION_FAILURE,
            "The system could not verify all citations to source documents. "
            f"{verification.invalid_citations} out of {verification.total_citations} citations failed validation. "
            "This indicates the answer may contain inaccurate references or hallucinated information. "
            "For legal reliability, we cannot provide an answer with unverified citations."
        )
    
    # Check critical risk
    if risk and risk.overall_risk == "critical":
        return (
            RefusalReason.HIGH_RISK,
            "This query involves critical legal risk factors that require professional legal counsel. "
            f"Risk factors identified: {', '.join(risk.risk_factors[:3])}. "
            "The system cannot safely provide guidance on matters with such high liability exposure."
        )
    
    # Check confidence
    if confidence and confidence.overall_score < settings.low_confidence_threshold:
        return (
            RefusalReason.LOW_CONFIDENCE,
            f"Confidence score ({confidence.overall_score:.1f}/100) is below the minimum threshold "
            f"({settings.low_confidence_threshold}/100) for providing answers. "
            f"Reasoning: {confidence.reasoning}"
        )
    
    # Check jurisdictional conflicts
    if counter_args and counter_args.jurisdictional_issues:
        return (
            RefusalReason.JURISDICTIONAL_CONFLICT,
            "Significant jurisdictional conflicts or ambiguities were identified. "
            f"Issues: {', '.join(counter_args.jurisdictional_issues[:2])}. "
            "Legal answers are highly jurisdiction-specific, and these conflicts prevent a reliable answer."
        )
    
    # Check missing context
    if counter_args and len(counter_args.missing_context) > 2:
        return (
            RefusalReason.INSUFFICIENT_CONTEXT,
            "Insufficient context to provide a reliable answer. "
            f"Missing information: {', '.join(counter_args.missing_context[:3])}. "
            "Legal analysis requires complete context to avoid misleading guidance."
        )
    
    # Default
    return (
        RefusalReason.LOW_CONFIDENCE,
        "The system could not generate a sufficiently confident answer to this query."
    )


def _create_default_confidence():
    """Create default confidence score for error cases."""
    from ..schemas.scoring import ConfidenceScore
    return ConfidenceScore(
        overall_score=0.0,
        factors={},
        reasoning="No confidence assessment available due to system error"
    )


def _create_default_risk():
    """Create default risk assessment for error cases."""
    from ..schemas.scoring import RiskAssessment
    return RiskAssessment(
        overall_risk="critical",
        risk_factors=["Unable to assess risk"],
        mitigation_suggestions=["Consult legal counsel"],
        liability_concerns=["Risk assessment unavailable"]
    )


def _create_default_verification():
    """Create default verification result for error cases."""
    from ..schemas.verification import VerificationResult
    return VerificationResult(
        all_citations_valid=False,
        citation_validations=[],
        total_citations=0,
        valid_citations=0,
        invalid_citations=0,
        verification_issues=["Verification not performed"]
    )

