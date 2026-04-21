"""
Counter-argument schemas - Output from the Counter-Argument Agent.

Critical design: Adversarial validation.

Why this exists:
- LLMs are overconfident
- Legal reasoning has exceptions
- Context windows miss edge cases

The counter-agent's job: Try to break the answer.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CounterArgument(BaseModel):
    """
    Counter-arguments attempting to invalidate the main answer.
    
    Why adversarial agents matter:
    - Surfaces contradictions
    - Highlights jurisdictional issues
    - Finds overlooked exceptions
    - Reduces confirmation bias
    
    Design pattern: "Red Team" approach
    - Main agent = Blue Team (construct answer)
    - Counter agent = Red Team (attack answer)
    - Verification agent = Judge (validate both)
    
    Common mistake:
    ❌ Counter-agent just rephrases answer (useless)
    ✅ Counter-agent actively seeks contradictions (valuable)
    """
    contradictions: List[str] = Field(
        default_factory=list,
        description="Contradicting clauses or principles found"
    )
    exceptions: List[str] = Field(
        default_factory=list,
        description="Exceptions or carve-outs that might apply"
    )
    jurisdictional_issues: List[str] = Field(
        default_factory=list,
        description="Jurisdiction-specific problems (e.g., CA vs Federal law)"
    )
    ambiguities: List[str] = Field(
        default_factory=list,
        description="Ambiguous language that could be interpreted differently"
    )
    missing_context: List[str] = Field(
        default_factory=list,
        description="Information needed but not present in retrieved context"
    )
    alternative_interpretation: Optional[str] = Field(
        default=None,
        description="Alternative reasonable interpretation of the clauses"
    )
    severity: str = Field(
        ...,
        description="How serious are these counter-arguments? (minor/moderate/severe)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "contradictions": [],
                "exceptions": [
                    "Section 12.3(b) may exempt claims brought under the PAGA statute"
                ],
                "jurisdictional_issues": [
                    "California AB 51 restricts mandatory arbitration in employment"
                ],
                "ambiguities": [
                    "The term 'dispute' is not explicitly defined"
                ],
                "missing_context": [
                    "We don't have the full text of Section 12.3(b) and (c)"
                ],
                "alternative_interpretation": "The clause might only apply to contractual disputes, not statutory claims",
                "severity": "moderate"
            }
        }

