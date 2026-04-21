"""
GraphState - The central state flowing through our LangGraph state machine.

This is THE most important schema.

Why TypedDict for LangGraph state:
- LangGraph requires dict-like state
- TypedDict provides type hints without runtime overhead
- Each agent reads/writes specific keys

Design principle: Immutable progression.
- Each agent adds to state, never removes
- Full audit trail of what happened when
- Easy to debug: inspect state at any node

Common mistake to avoid:
❌ Mutating nested objects in-place (breaks tracing)
✅ Create new objects, add to state
"""

from typing import TypedDict, Optional, List
from typing_extensions import Annotated

from .query import Query
from .retrieval import RetrievalResult
from .answer import Answer
from .counter import CounterArgument
from .verification import VerificationResult
from .scoring import ConfidenceScore, RiskAssessment
from .response import FinalResponse


class GraphState(TypedDict, total=False):
    """
    The state flowing through our LangGraph agents.
    
    State flow:
    1. START → query added
    2. Classification → query.query_type, query.jurisdiction populated
    3. Retrieval → retrieval_result added
    4. Answer Agent → answer added
    5. Counter Agent → counter_arguments added
    6. Verification → verification_result added
    7. Scoring → confidence, risk added
    8. Decision Gate → final_response added or refusal logic
    9. END
    
    Why total=False:
    - Fields populate progressively
    - Early nodes don't have later fields yet
    - Allows type checking without requiring all fields
    
    LangGraph reducer pattern:
    - By default, updates replace values
    - Can use Annotated for custom reducers (e.g., append to list)
    """
    
    # Input
    query: Query
    
    # Retrieval
    retrieval_result: Optional[RetrievalResult]
    
    # Agent outputs
    answer: Optional[Answer]
    counter_arguments: Optional[CounterArgument]
    
    # Validation & scoring
    verification_result: Optional[VerificationResult]
    confidence: Optional[ConfidenceScore]
    risk: Optional[RiskAssessment]
    
    # Decision & output
    should_answer: Optional[bool]  # Decision gate result
    final_response: Optional[FinalResponse]
    
    # Metadata
    query_id: str
    error: Optional[str]  # If something goes wrong

