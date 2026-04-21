"""
Retrieval schemas - What we get from the vector store.

Design principle: Clause-aware chunking.
Every chunk MUST preserve:
- Clause ID (for verification)
- Exact text (for citation matching)
- Metadata (for filtering)

Common mistake to avoid:
❌ Chunking mid-sentence or splitting clauses
✅ Chunk boundaries = clause boundaries
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class RetrievedClause(BaseModel):
    """
    A single retrieved clause from the vector store.
    
    Why these fields:
    - clause_id: Unique identifier for verification (e.g., "SEC_12.3")
    - text: Exact verbatim text (no summarization)
    - document_id: Source document for audit trail
    - section: Human-readable location (e.g., "Arbitration Agreement")
    - similarity_score: Vector similarity (for debugging, not decision-making)
    - metadata: Jurisdiction, document type, effective date, etc.
    """
    clause_id: str = Field(..., description="Unique clause identifier (e.g., 'DOC1_SEC12_CLAUSE3')")
    text: str = Field(..., description="Exact verbatim clause text")
    document_id: str = Field(..., description="Source document identifier")
    section: str = Field(..., description="Section heading or number")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Vector similarity score")
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata (jurisdiction, doc_type, date, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "clause_id": "EMP_AGREE_001_SEC12.3",
                "text": "Any dispute arising under this Agreement shall be resolved through binding arbitration...",
                "document_id": "EMP_AGREE_001",
                "section": "Section 12.3 - Dispute Resolution",
                "similarity_score": 0.89,
                "metadata": {
                    "jurisdiction": "California",
                    "document_type": "employment_agreement",
                    "effective_date": "2023-01-15"
                }
            }
        }


class RetrievalResult(BaseModel):
    """
    Collection of retrieved clauses with retrieval metadata.
    
    Why top_k matters:
    - Too few → Miss relevant context
    - Too many → Noise + cost + confusion
    - Typical range: 5-10 for legal RAG
    """
    clauses: List[RetrievedClause] = Field(..., description="Retrieved clauses ranked by relevance")
    top_k: int = Field(..., description="Number of clauses retrieved")
    retrieval_query: str = Field(..., description="Query used for retrieval (may differ from user query)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "clauses": [],  # Would contain RetrievedClause examples
                "top_k": 5,
                "retrieval_query": "arbitration employment disputes California"
            }
        }

