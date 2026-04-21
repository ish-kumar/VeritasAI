"""
Answer schemas - Output from the Answer Agent.

Critical principle: EVERY claim must be cited.

Design decision: Structured citations prevent hallucinations.
- LLM must provide clause_id + quoted_text
- Verification agent checks these match exactly
"""

from typing import List
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """
    A citation linking an answer claim to source text.
    
    Why both clause_id AND quoted_text:
    - clause_id: Points to source (verifiable)
    - quoted_text: Exact snippet (prevents paraphrasing errors)
    - reasoning: Why this citation supports the claim (explainability)
    - document_id: Source document (transparency)
    
    Common mistake:
    ❌ Just clause_id → Can't verify LLM read it correctly
    ✅ Both → Can check verbatim match
    """
    clause_id: str = Field(..., description="Clause ID from retrieved context")
    quoted_text: str = Field(..., description="Exact text quoted from the clause")
    reasoning: str = Field(..., description="Why this citation supports the answer")
    document_id: str = Field(default="", description="Source document identifier for transparency")
    
    class Config:
        json_schema_extra = {
            "example": {
                "clause_id": "EMP_AGREE_001_SEC12.3",
                "quoted_text": "Any dispute arising under this Agreement shall be resolved through binding arbitration",
                "reasoning": "This clause explicitly mandates arbitration for all disputes under the agreement",
                "document_id": "EMP_AGREE_001"
            }
        }


class Answer(BaseModel):
    """
    The Answer Agent's response to the legal query.
    
    Why structured like this:
    - answer_text: The actual answer (human-readable)
    - citations: Grounding in source documents (verifiable)
    - reasoning: Logical steps taken (explainable)
    - assumptions: What the answer depends on (auditable)
    - caveats: Limitations or exceptions (safe)
    
    Production requirement: Never answer without citations (except error cases).
    Note: min_length=0 allows error responses with no citations
    """
    answer_text: str = Field(..., description="The legal answer or interpretation")
    citations: List[Citation] = Field(default_factory=list, description="Citations supporting the answer")
    reasoning: str = Field(..., description="Step-by-step reasoning process")
    assumptions: List[str] = Field(
        default_factory=list,
        description="Assumptions made in arriving at this answer"
    )
    caveats: List[str] = Field(
        default_factory=list,
        description="Limitations, exceptions, or warnings"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer_text": "Yes, the arbitration clause in Section 12.3 applies to employment disputes.",
                "citations": [],  # Would contain Citation examples
                "reasoning": "The clause states 'any dispute' without carving out employment matters...",
                "assumptions": [
                    "The employment agreement is valid and enforceable",
                    "California law permits arbitration of employment disputes"
                ],
                "caveats": [
                    "Certain statutory claims may be exempt from arbitration under CA law"
                ]
            }
        }

