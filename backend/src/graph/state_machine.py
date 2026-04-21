"""
LangGraph State Machine - The orchestration engine.

This is THE core of our system.

Design philosophy:
- Each node = one agent or decision point
- State flows immutably through nodes
- Conditional edges for decision logic
- Human-in-loop ready (can pause anywhere)

Why LangGraph vs vanilla LangChain:
1. Explicit state management (no hidden mutations)
2. Conditional routing (if/else logic)
3. Cycles/loops (for iterative refinement)
4. Debuggability (inspect state at each node)
5. Production-ready patterns (error handling, retries, timeouts)

Common mistakes to avoid:
❌ Mutating state in-place → breaks immutability
❌ Side effects in nodes → hard to test
❌ No error handling → silent failures
✅ Pure functions that return new state
✅ Explicit error nodes
✅ Comprehensive logging
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from loguru import logger

from ..schemas.state import GraphState
from ..utils.config import get_settings


def create_legal_rag_graph() -> StateGraph:
    """
    Create the Legal RAG state machine.
    
    Graph structure:
    
    START
      ↓
    classify_query → Determine query type & jurisdiction
      ↓
    retrieve_clauses → Fetch relevant legal clauses
      ↓
    generate_answer → Answer Agent produces grounded answer
      ↓
    generate_counter → Counter-Argument Agent challenges answer
      ↓
    verify_citations → Verify all citations are accurate
      ↓
    score_confidence → Compute confidence & risk scores
      ↓
    decision_gate → Should we answer?
      ↓              ↓
    Yes            No
      ↓              ↓
    format_answer  format_refusal
      ↓              ↓
    END            END
    
    Design decisions:
    1. Linear flow for MVP (can add cycles later for refinement)
    2. Decision gate at the end (easier to reason about)
    3. Separate formatting nodes (clean separation of logic vs presentation)
    
    Why this order:
    - Classification first → routes appropriately
    - Retrieval before reasoning → grounded in documents
    - Answer before counter → need something to challenge
    - Verification after both → validates complete reasoning
    - Scoring after verification → incorporates all signals
    - Decision at end → all information available
    """
    
    # Import node functions (we'll implement these next)
    from ..agents.classifier import classify_query_node
    from ..agents.retriever import retrieve_clauses_node
    from ..agents.answer import generate_answer_node
    from ..agents.counter import generate_counter_node
    from ..agents.verifier import verify_citations_node
    from ..agents.scorer import score_confidence_node
    from .decision_gate import decision_gate_node
    from .formatters import format_answer_node, format_refusal_node
    
    # Create the graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("classify_query", classify_query_node)
    workflow.add_node("retrieve_clauses", retrieve_clauses_node)
    workflow.add_node("generate_answer", generate_answer_node)
    workflow.add_node("generate_counter", generate_counter_node)
    workflow.add_node("verify_citations", verify_citations_node)
    workflow.add_node("score_confidence", score_confidence_node)
    workflow.add_node("decision_gate", decision_gate_node)
    workflow.add_node("format_answer", format_answer_node)
    workflow.add_node("format_refusal", format_refusal_node)
    
    # Set entry point
    workflow.set_entry_point("classify_query")
    
    # Add edges (linear flow)
    workflow.add_edge("classify_query", "retrieve_clauses")
    workflow.add_edge("retrieve_clauses", "generate_answer")
    workflow.add_edge("generate_answer", "generate_counter")
    workflow.add_edge("generate_counter", "verify_citations")
    workflow.add_edge("verify_citations", "score_confidence")
    workflow.add_edge("score_confidence", "decision_gate")
    
    # Add conditional edges from decision gate
    workflow.add_conditional_edges(
        "decision_gate",
        route_decision,
        {
            "answer": "format_answer",
            "refuse": "format_refusal",
        }
    )
    
    # Both formatters lead to END
    workflow.add_edge("format_answer", END)
    workflow.add_edge("format_refusal", END)
    
    return workflow


def route_decision(state: GraphState) -> Literal["answer", "refuse"]:
    """
    Route decision: should we answer or refuse?
    
    Decision logic:
    1. Check if decision_gate set should_answer flag
    2. Route accordingly
    
    Why separate function:
    - Clean separation of routing logic
    - Easy to test independently
    - Can add more complex logic later (e.g., human-in-loop)
    
    LangGraph pattern:
    - Conditional edges call a function
    - Function returns string key
    - Key maps to next node in the graph
    """
    should_answer = state.get("should_answer", False)
    
    if should_answer:
        logger.info(f"Decision gate: ANSWER (query_id: {state.get('query_id')})")
        return "answer"
    else:
        logger.info(f"Decision gate: REFUSE (query_id: {state.get('query_id')})")
        return "refuse"


# Compile the graph (singleton)
_compiled_graph = None


def get_compiled_graph():
    """
    Get compiled graph singleton.
    
    Why compile:
    - LangGraph validates the graph structure
    - Optimizes execution plan
    - Catches errors early
    
    Why singleton:
    - Compilation is expensive
    - Graph is stateless (state flows through it)
    - Share across all requests
    """
    global _compiled_graph
    if _compiled_graph is None:
        workflow = create_legal_rag_graph()
        _compiled_graph = workflow.compile()
        logger.info("LangGraph compiled successfully")
    return _compiled_graph


async def run_legal_rag_query(query_text: str, jurisdiction: str = None, context: str = None) -> dict:
    """
    Execute the Legal RAG pipeline.
    
    This is the main entry point for processing queries.
    
    Args:
        query_text: The user's legal question
        jurisdiction: Optional jurisdiction context
        context: Optional additional context
    
    Returns:
        The final response (FinalResponse schema)
    
    Design decisions:
    1. Async for scalability (can handle many concurrent queries)
    2. Initialize state here (separation of concerns)
    3. Return final_response from state (clean interface)
    
    Error handling strategy:
    - Try to complete pipeline even with errors
    - Log errors but don't crash
    - Return error in final_response if needed
    """
    import uuid
    from ..schemas.query import Query
    
    # Generate unique query ID
    query_id = f"qry_{uuid.uuid4().hex[:12]}"
    
    # Initialize state
    initial_state: GraphState = {
        "query": Query(
            text=query_text,
            jurisdiction=jurisdiction,
            context=context,
        ),
        "query_id": query_id,
    }
    
    logger.info(f"Starting Legal RAG query: {query_id}")
    logger.debug(f"Query text: {query_text}")
    
    try:
        # Get compiled graph
        graph = get_compiled_graph()
        
        # Execute the graph
        # Note: LangGraph returns the final state after execution
        final_state = await graph.ainvoke(initial_state)
        
        logger.info(f"Legal RAG query completed: {query_id}")
        
        # Return the final response
        return final_state.get("final_response")
        
    except Exception as e:
        logger.error(f"Error in Legal RAG query {query_id}: {str(e)}")
        logger.exception(e)
        
        # Return error response
        from ..schemas.response import FinalResponse, RefusalReason
        from ..schemas.scoring import ConfidenceScore, RiskAssessment
        from ..schemas.verification import VerificationResult
        
        return FinalResponse(
            success=False,
            refusal_reason=RefusalReason.OUT_OF_SCOPE,
            refusal_explanation=f"System error: {str(e)}",
            confidence=ConfidenceScore(
                overall_score=0.0,
                factors={},
                reasoning="System error prevented scoring"
            ),
            risk=RiskAssessment(
                overall_risk="critical",
                risk_factors=["System error"],
                mitigation_suggestions=["Contact system administrator"],
                liability_concerns=["Unable to process query safely"]
            ),
            verification=VerificationResult(
                all_citations_valid=False,
                citation_validations=[],
                total_citations=0,
                valid_citations=0,
                invalid_citations=0,
                verification_issues=[f"System error: {str(e)}"]
            ),
            warnings=["System error occurred"],
            next_steps=["Try again later or contact support"],
            query_id=query_id,
        )

