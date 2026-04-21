"""
Response schemas - Final output to user.

Design principle: Radical transparency.

The user should see:
- The answer (if confident enough)
- Why we're confident (or not)
- What we're worried about (risks)
- All citations (with exact quotes)
- The entire reasoning chain (explainability)

This isn't just good UX - it's legal necessity.
"""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

from .answer import Answer
from .counter import CounterArgument
from .verification import VerificationResult
from .scoring import ConfidenceScore, RiskAssessment


class RefusalReason(str, Enum):
    """
    Why we might refuse to answer.
    
    Design decision: Explicit refusal categories.
    - Helps users understand what's missing
    - Helps us debug system issues
    - Helps us measure refusal rate by category
    """
    LOW_CONFIDENCE = "low_confidence"
    HIGH_RISK = "high_risk"
    CITATION_FAILURE = "citation_failure"
    INSUFFICIENT_CONTEXT = "insufficient_context"
    JURISDICTIONAL_CONFLICT = "jurisdictional_conflict"
    OUT_OF_SCOPE = "out_of_scope"


class FinalResponse(BaseModel):
    """
    The complete response to the user.
    
    Philosophy: Show your work.
    
    Why include everything:
    - Legal professionals need to verify
    - Debugging requires full trace
    - Explainability builds trust
    - Audit trails protect everyone
    
    Design decision: Always include intermediate steps.
    Even if we refuse to answer, show:
    - What we retrieved
    - What we tried to answer
    - What went wrong
    - What would help
    """
    # Core response
    success: bool = Field(..., description="Did we provide an answer?")
    answer: Optional[Answer] = Field(default=None, description="The answer (if success=True)")
    refusal_reason: Optional[RefusalReason] = Field(
        default=None,
        description="Why we refused (if success=False)"
    )
    refusal_explanation: Optional[str] = Field(
        default=None,
        description="Human-readable refusal explanation"
    )
    
    # Scoring & risk
    confidence: ConfidenceScore = Field(..., description="Confidence assessment")
    risk: RiskAssessment = Field(..., description="Risk assessment")
    
    # Intermediate steps (for explainability)
    counter_arguments: Optional[CounterArgument] = Field(
        default=None,
        description="Counter-arguments considered"
    )
    verification: VerificationResult = Field(..., description="Citation verification results")
    
    # Recommendations
    warnings: List[str] = Field(
        default_factory=list,
        description="Warnings for the user (e.g., 'Consult attorney')"
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="Suggested next steps"
    )
    
    # Metadata
    query_id: str = Field(..., description="Unique query identifier (for tracking)")
    processing_time_ms: Optional[float] = Field(
        default=None,
        description="Total processing time"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "answer": None,  # Would be Answer object
                "refusal_reason": None,
                "refusal_explanation": None,
                "confidence": None,  # Would be ConfidenceScore object
                "risk": None,  # Would be RiskAssessment object
                "counter_arguments": None,
                "verification": None,  # Would be VerificationResult object
                "warnings": [
                    "This interpretation may be affected by recent California legislation",
                    "Consult employment attorney before relying on this analysis"
                ],
                "next_steps": [
                    "Review full text of Section 12.3",
                    "Check recent case law on AB 51"
                ],
                "query_id": "qry_20260106_001",
                "processing_time_ms": 2341.5
            }
        }

