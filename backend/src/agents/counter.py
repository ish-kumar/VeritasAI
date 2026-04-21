"""
Counter-Argument Agent - Real LLM Implementation

This node:
1. Extracts the answer and retrieved clauses from state
2. Builds adversarial prompt to challenge the answer
3. Calls LLM to find weaknesses and alternatives
4. Parses structured counter-arguments
5. Assesses severity of concerns

Design philosophy: Red Team thinking
- Actively seek problems, don't just agree
- Find legitimate concerns, not pedantic issues
- Provide alternative interpretations
- Assess real impact (severity)
"""

from pathlib import Path
from loguru import logger

from ..schemas.state import GraphState
from ..schemas.counter import CounterArgument
from ..schemas.answer import Answer
from ..schemas.retrieval import RetrievalResult
from ..schemas.query import Query
from ..utils.llm_client import get_llm_client


# Load prompt templates
PROMPTS_DIR = Path(__file__).parent / "prompts"
SYSTEM_PROMPT = (PROMPTS_DIR / "counter_system.txt").read_text()
USER_TEMPLATE = (PROMPTS_DIR / "counter_user_template.txt").read_text()


def format_citations_for_prompt(answer: Answer) -> str:
    """
    Format citations for counter-agent review.
    
    Design decision: Show what the Answer Agent cited.
    - Counter-agent can check if citations support claims
    - Can identify if important clauses were ignored
    - Can spot if reasoning is faithful to citations
    """
    if not answer.citations:
        return "No citations provided."
    
    citations_text = []
    for i, cite in enumerate(answer.citations, 1):
        citations_text.append(
            f"[{i}] Clause: {cite.clause_id}\n"
            f"    Quote: \"{cite.quoted_text}\"\n"
            f"    Reasoning: {cite.reasoning}"
        )
    
    return "\n\n".join(citations_text)


def format_context_for_counter(retrieval_result: RetrievalResult) -> str:
    """
    Format retrieved clauses for counter-agent analysis.
    
    Design decision: Give counter-agent full context.
    - Can spot clauses that answer-agent missed
    - Can find contradictions
    - Can identify exceptions
    
    Same format as answer agent for consistency.
    """
    context_parts = []
    
    for i, clause in enumerate(retrieval_result.clauses, 1):
        context_part = f"""[Clause {i}]
ID: {clause.clause_id}
Section: {clause.section}
Text: "{clause.text}"
Metadata: {clause.metadata}
"""
        context_parts.append(context_part)
    
    return "\n".join(context_parts)


async def generate_counter_node(state: GraphState) -> GraphState:
    """
    Generate counter-arguments to challenge the answer.
    
    Flow:
    1. Extract answer and context from state
    2. Build adversarial prompt
    3. Call LLM (same model as answer agent)
    4. Parse counter-arguments
    5. Handle errors gracefully
    
    Error handling:
    - If no answer exists → Return minimal counter-arguments
    - If LLM fails → Log error, return safe default
    - If parsing fails → Return default with severity "moderate"
    
    Args:
        state: GraphState with answer and retrieval_result
    
    Returns:
        Updated state with counter_arguments field
    """
    query_id = state.get("query_id")
    query: Query = state.get("query")
    answer: Answer = state.get("answer")
    retrieval_result: RetrievalResult = state.get("retrieval_result")
    
    logger.info(f"Generating counter-arguments: {query_id}")
    
    # Validation: Check we have an answer to challenge
    if not answer:
        logger.warning(f"No answer to challenge: {query_id}")
        # Return minimal counter-arguments
        no_answer_counter = CounterArgument(
            contradictions=[],
            exceptions=[],
            jurisdictional_issues=[],
            ambiguities=[],
            missing_context=["No answer was generated"],
            alternative_interpretation=None,
            severity="severe"  # No answer is a severe issue
        )
        return {
            **state,
            "counter_arguments": no_answer_counter,
        }
    
    # Build context and citations
    context = format_context_for_counter(retrieval_result)
    citations = format_citations_for_prompt(answer)
    
    # Build user prompt from template
    user_prompt = USER_TEMPLATE.format(
        question=query.text,
        answer_text=answer.answer_text,
        citations=citations,
        reasoning=answer.reasoning,
        context=context
    )
    
    logger.debug(f"Counter-agent prompt built: {len(user_prompt)} chars")
    
    try:
        # Get LLM client
        client = get_llm_client()
        
        # Generate counter-arguments with structured output
        counter: CounterArgument = await client.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=CounterArgument,
            max_tokens=1500,  # Counter-arguments can be detailed
        )
        
        logger.info(
            f"Counter-arguments generated: {query_id}, "
            f"severity={counter.severity}, "
            f"contradictions={len(counter.contradictions)}, "
            f"exceptions={len(counter.exceptions)}"
        )
        
        # Log if severe issues found
        if counter.severity == "severe":
            logger.warning(
                f"Severe counter-arguments found for {query_id}: "
                f"contradictions={counter.contradictions}, "
                f"exceptions={counter.exceptions}"
            )
        
        return {
            **state,
            "counter_arguments": counter,
        }
    
    except ValueError as e:
        # LLM returned invalid format
        logger.error(f"LLM returned invalid format for counter-arguments: {query_id}: {e}")
        # Return default counter-arguments indicating system issue
        error_counter = CounterArgument(
            contradictions=[],
            exceptions=[],
            jurisdictional_issues=[],
            ambiguities=["Counter-argument analysis unavailable (model output format error)."],
            missing_context=["The system could not parse the counter-agent output into the expected schema."],
            alternative_interpretation=None,
            severity="moderate"  # Err on side of caution
        )
        return {
            **state,
            "counter_arguments": error_counter,
            "error": f"Counter-agent format error: {str(e)}"
        }
    
    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error generating counter-arguments: {query_id}: {type(e).__name__}: {e}")
        logger.exception(e)
        # Return safe default
        error_counter = CounterArgument(
            contradictions=[],
            exceptions=[],
            jurisdictional_issues=[],
            ambiguities=["System error during counter-argument generation"],
            missing_context=["Unable to complete analysis"],
            alternative_interpretation=None,
            severity="moderate"
        )
        return {
            **state,
            "counter_arguments": error_counter,
            "error": f"Counter-agent error: {str(e)}"
        }

