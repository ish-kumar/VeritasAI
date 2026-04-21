"""
Verification schemas - Citation and grounding validation.

Core principle: Trust but verify.

Why this is non-negotiable:
- LLMs hallucinate citations
- Legal work requires accuracy
- Ungrounded claims = liability
"""

from typing import List
from pydantic import BaseModel, Field


class CitationValidation(BaseModel):
    """
    Validation result for a single citation.
    
    Verification checks:
    1. Does clause_id exist in retrieved context?
    2. Does quoted_text appear verbatim in that clause?
    3. Is the reasoning faithful to the text?
    
    Why strict verbatim matching:
    - LLMs paraphrase incorrectly
    - Legal text is precise (one word changes meaning)
    - We need 100% accuracy for citations
    
    Design decision: Fail closed, not open.
    If verification fails → penalize confidence heavily
    """
    citation_id: str = Field(..., description="Identifier for this citation (for tracing)")
    clause_id: str = Field(..., description="The clause being cited")
    is_valid: bool = Field(..., description="Does the citation pass verification?")
    quoted_text_found: bool = Field(..., description="Was the quoted text found verbatim?")
    reasoning_faithful: bool = Field(..., description="Is the reasoning faithful to the text?")
    error_message: str = Field(
        default="",
        description="If invalid, what went wrong?"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "citation_id": "cite_001",
                "clause_id": "EMP_AGREE_001_SEC12.3",
                "is_valid": True,
                "quoted_text_found": True,
                "reasoning_faithful": True,
                "error_message": ""
            }
        }


class VerificationResult(BaseModel):
    """
    Overall verification result for an answer.
    
    Why aggregate metrics matter:
    - Single failed citation → entire answer suspect
    - Partial grounding → lower confidence
    - All citations valid → high confidence
    """
    all_citations_valid: bool = Field(..., description="Do all citations pass?")
    citation_validations: List[CitationValidation] = Field(
        ...,
        description="Per-citation validation results"
    )
    total_citations: int = Field(..., description="Total citations checked")
    valid_citations: int = Field(..., description="Number of valid citations")
    invalid_citations: int = Field(..., description="Number of invalid citations")
    verification_issues: List[str] = Field(
        default_factory=list,
        description="Issues found during verification"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "all_citations_valid": False,
                "citation_validations": [],
                "total_citations": 3,
                "valid_citations": 2,
                "invalid_citations": 1,
                "verification_issues": [
                    "Citation cite_002: Quoted text not found verbatim in clause"
                ]
            }
        }

