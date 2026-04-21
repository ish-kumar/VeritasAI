"""
Answer Agent - Real LLM Implementation

This node:
1. Extracts query and retrieved clauses from state
2. Builds prompt from templates
3. Calls LLM (Groq/OpenAI/Anthropic)
4. Parses structured output
5. Validates answer quality
6. Returns Answer object

Design decisions:
- Use prompt templates (easy to iterate)
- Structured output (Pydantic validation)
- Graceful error handling (fail safely)
- Detailed logging (observability)
"""

import os
from pathlib import Path
from loguru import logger

from ..schemas.state import GraphState
from ..schemas.answer import Answer, Citation
from ..schemas.retrieval import RetrievalResult
from ..schemas.query import Query
from ..utils.llm_client import get_llm_client


# Load prompt templates
PROMPTS_DIR = Path(__file__).parent / "prompts"
SYSTEM_PROMPT = (PROMPTS_DIR / "answer_system.txt").read_text()
USER_TEMPLATE = (PROMPTS_DIR / "answer_user_template.txt").read_text()


def format_context(retrieval_result: RetrievalResult) -> str:
    """
    Format retrieved clauses for LLM context.
    
    Design decision: Structured format with clear boundaries.
    - Each clause clearly labeled
    - Metadata included (jurisdiction, document)
    - Easy for LLM to parse and cite
    
    Example output:
    [Source 1]
    ID: SEC_12.3
    Section: Dispute Resolution
    Text: "Any dispute arising under..."
    Metadata: {"jurisdiction": "California"}
    
    [Clause 2]
    ...
    """
    context_parts = []
    
    for i, clause in enumerate(retrieval_result.clauses, 1):
        context_part = f"""[Source {i}]
ID: {clause.clause_id}
Section: {clause.section}
Text: "{clause.text}"
Metadata: {clause.metadata}
"""
        context_parts.append(context_part)
    
    return "\n".join(context_parts)


async def generate_answer_node(state: GraphState) -> GraphState:
    """
    Generate answer using LLM with retrieved context.
    
    Flow:
    1. Extract query and clauses from state
    2. Build prompt with context
    3. Call LLM
    4. Parse and validate output
    5. Handle errors gracefully
    
    Error handling:
    - LLM timeout → Retries automatically (in LLMClient)
    - Invalid output → Log error, return safe refusal
    - No clauses → Return "insufficient context" response
    
    Args:
        state: GraphState with query and retrieval_result
    
    Returns:
        Updated state with answer field
    """
    query_id = state.get("query_id")
    query: Query = state.get("query")
    retrieval_result: RetrievalResult = state.get("retrieval_result")
    
    logger.info(f"Generating answer with LLM: {query_id}")
    
    # Validation: Check we have retrieved clauses
    if not retrieval_result or not retrieval_result.clauses:
        logger.warning(f"No clauses retrieved for query: {query_id}")
        # Return a safe answer indicating insufficient context
        no_context_answer = Answer(
            answer_text="Insufficient context to answer this question. No relevant legal clauses were found.",
            citations=[],
            reasoning="No legal clauses were retrieved that relate to this question.",
            assumptions=["The question requires specific legal document context"],
            caveats=["Cannot provide an answer without relevant legal documents"]
        )
        return {
            **state,
            "answer": no_context_answer,
        }
    
    # Build context from retrieved clauses
    context = format_context(retrieval_result)
    
    # Build additional context
    additional_context = ""
    if query.jurisdiction:
        additional_context += f"\nJurisdiction: {query.jurisdiction}"
    if query.context:
        additional_context += f"\nAdditional Context from User: {query.context}"
    
    # Build user prompt from template
    user_prompt = USER_TEMPLATE.format(
        context=context,
        question=query.text,
        additional_context=additional_context
    )
    
    logger.debug(f"Prompt built: system={len(SYSTEM_PROMPT)} chars, user={len(user_prompt)} chars")
    
    try:
        # Get LLM client
        client = get_llm_client()
        
        # Generate answer with structured output
        answer: Answer = await client.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=Answer,
            max_tokens=2000,
        )
        
        logger.info(
            f"Answer generated: {query_id}, "
            f"citations={len(answer.citations)}, "
            f"answer_len={len(answer.answer_text)}"
        )
        
        # Validation: Check answer quality
        if len(answer.citations) == 0:
            logger.warning(f"Answer has no citations: {query_id}")
            # Add a caveat
            answer.caveats.append("This answer lacks specific citations to source documents")
        
        if len(answer.answer_text) < 20:
            logger.warning(f"Answer is very short: {query_id}")
        
        return {
            **state,
            "answer": answer,
        }
    
    except ValueError as e:
        # LLM returned invalid format
        logger.error(f"LLM returned invalid format for {query_id}: {e}")
        # Return safe refusal
        error_answer = Answer(
            answer_text="Unable to generate a properly formatted answer due to a system error.",
            citations=[],
            reasoning="The system encountered an error parsing the LLM response.",
            assumptions=[],
            caveats=["System error occurred", "Please try rephrasing your question"]
        )
        return {
            **state,
            "answer": error_answer,
            "error": f"LLM format error: {str(e)}"
        }
    
    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error generating answer for {query_id}: {type(e).__name__}: {e}")
        logger.exception(e)
        # Return safe refusal
        error_answer = Answer(
            answer_text="Unable to generate an answer due to a system error.",
            citations=[],
            reasoning="An unexpected error occurred during answer generation.",
            assumptions=[],
            caveats=["System error occurred", "Please contact support if this persists"]
        )
        return {
            **state,
            "answer": error_answer,
            "error": f"Unexpected error: {str(e)}"
        }


# For backward compatibility (some code might still use sync version)
# In production, everything should be async
def generate_answer_node_sync(state: GraphState) -> GraphState:
    """
    Synchronous wrapper for generate_answer_node.
    
    Note: LangGraph supports async nodes natively,
    so this is mainly for testing or backward compatibility.
    """
    import asyncio
    return asyncio.run(generate_answer_node(state))

