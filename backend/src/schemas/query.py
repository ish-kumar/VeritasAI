"""
Query schemas - Entry point for user questions.

Design decision: Classify queries early to route appropriately.
- Simple queries → fast path
- Complex queries → full adversarial pipeline
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class QueryType(str, Enum):
    """
    Query classification types.
    
    Why this matters:
    - FACTUAL: "What is the definition of X?" → Retrieval-heavy
    - INTERPRETIVE: "Does this clause apply?" → Reasoning-heavy
    - COMPARATIVE: "Which is stronger?" → Multi-document
    - PROCEDURAL: "What steps are required?" → Sequential logic
    """
    FACTUAL = "factual"
    INTERPRETIVE = "interpretive"
    COMPARATIVE = "comparative"
    PROCEDURAL = "procedural"
    UNKNOWN = "unknown"


class Query(BaseModel):
    """
    User query with metadata.
    
    Why we capture this:
    - text: The actual question
    - query_type: Determines agent behavior
    - jurisdiction: Critical for legal context
    - context: User-provided background (optional)
    """
    text: str = Field(..., description="The user's legal question")
    query_type: Optional[QueryType] = Field(
        default=None,
        description="Classified query type (populated by classification agent)"
    )
    jurisdiction: Optional[str] = Field(
        default=None,
        description="Legal jurisdiction (e.g., 'US Federal', 'California', 'EU')"
    )
    context: Optional[str] = Field(
        default=None,
        description="Additional context provided by user"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Does the arbitration clause in Section 12.3 apply to employment disputes?",
                "jurisdiction": "California",
                "context": "This is regarding a software engineer's employment agreement"
            }
        }

