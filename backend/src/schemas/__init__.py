"""
Core Pydantic schemas for the Legal RAG system.

These schemas serve as:
1. Type contracts between agents
2. LLM structured output definitions
3. API request/response models
4. Data validation boundaries
"""

from .state import GraphState
from .query import Query, QueryType
from .retrieval import RetrievedClause, RetrievalResult
from .answer import Answer, Citation
from .counter import CounterArgument
from .verification import VerificationResult, CitationValidation
from .scoring import ConfidenceScore, RiskAssessment
from .response import FinalResponse, RefusalReason

__all__ = [
    "GraphState",
    "Query",
    "QueryType",
    "RetrievedClause",
    "RetrievalResult",
    "Answer",
    "Citation",
    "CounterArgument",
    "VerificationResult",
    "CitationValidation",
    "ConfidenceScore",
    "RiskAssessment",
    "FinalResponse",
    "RefusalReason",
]

