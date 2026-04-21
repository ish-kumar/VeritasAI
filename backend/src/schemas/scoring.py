"""
Scoring schemas - Confidence and risk assessment.

Philosophy: Quantify uncertainty.

Why we need this:
- Not all answers are equal
- Users need to know what to trust
- System needs to decide when to refuse
"""

from typing import List, Dict
from pydantic import BaseModel, Field


class ConfidenceScore(BaseModel):
    """
    Confidence score with breakdown.
    
    Design decision: Composite score from multiple factors.
    
    Factors that increase confidence:
    - All citations verified ✓
    - Counter-arguments are weak ✓
    - Jurisdiction matches ✓
    - Query type is factual (not interpretive) ✓
    
    Factors that decrease confidence:
    - Failed citation verification ✗
    - Strong counter-arguments ✗
    - Jurisdictional conflicts ✗
    - Ambiguous language ✗
    - Missing context ✗
    
    Score ranges:
    - 85-100: High confidence → Answer normally
    - 60-84: Medium confidence → Answer with warnings
    - 0-59: Low confidence → Refuse with explanation
    """
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall confidence (0-100)")
    factors: Dict[str, float] = Field(
        ...,
        description="Breakdown of confidence factors"
    )
    reasoning: str = Field(..., description="Explanation of the confidence score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_score": 72.5,
                "factors": {
                    "citation_validity": 90.0,
                    "counter_argument_strength": 60.0,
                    "jurisdiction_match": 80.0,
                    "context_completeness": 70.0,
                    "query_complexity": 65.0
                },
                "reasoning": "Citations are valid but counter-arguments raise moderate concerns about jurisdiction"
            }
        }


class RiskAssessment(BaseModel):
    """
    Legal risk assessment for the answer.
    
    Why separate from confidence:
    - Confidence = "How sure are we?"
    - Risk = "What could go wrong?"
    
    These are orthogonal:
    - High confidence, low risk: Clear factual answer
    - High confidence, high risk: Clear answer to dangerous question
    - Low confidence, low risk: Uncertain but harmless
    - Low confidence, high risk: Uncertain and dangerous → REFUSE
    
    Risk categories:
    - Liability risk: Could this advice lead to legal liability?
    - Compliance risk: Does this touch regulated areas?
    - Ambiguity risk: Is the language open to multiple interpretations?
    """
    overall_risk: str = Field(
        ...,
        description="Overall risk level (low/medium/high/critical)"
    )
    risk_factors: List[str] = Field(
        default_factory=list,
        description="Specific risk factors identified"
    )
    mitigation_suggestions: List[str] = Field(
        default_factory=list,
        description="How to mitigate these risks (e.g., consult attorney)"
    )
    liability_concerns: List[str] = Field(
        default_factory=list,
        description="Potential liability issues"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_risk": "medium",
                "risk_factors": [
                    "Jurisdictional ambiguity between state and federal law",
                    "Recent case law may affect interpretation"
                ],
                "mitigation_suggestions": [
                    "Consult employment attorney in California",
                    "Review recent cases on AB 51"
                ],
                "liability_concerns": [
                    "Enforceability of arbitration clause is fact-specific"
                ]
            }
        }

