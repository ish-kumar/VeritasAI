"""
Query Classification Agent

Classifies queries using keyword/pattern-based heuristics.
This is fast, free (no LLM call), and effective for legal queries.

Classification criteria:
1. Query Type: factual, interpretive, comparative, procedural
2. Jurisdiction: Extract location/court mentions
3. Complexity: Based on query structure and keywords

Design: Lightweight heuristics > expensive LLM calls for classification.
"""

import re
from typing import Optional
from loguru import logger
from ..schemas.state import GraphState
from ..schemas.query import QueryType


def classify_query_node(state: GraphState) -> GraphState:
    """
    Classify the user query using pattern matching.
    
    Fast and accurate for most legal queries.
    """
    query_id = state.get("query_id")
    query = state.get("query")
    text = query.text.lower()
    
    logger.info(f"Classifying query: {query_id}")
    
    # 1. Classify query type
    query.query_type = _classify_query_type(text)
    
    # 2. Extract jurisdiction if mentioned
    if not query.jurisdiction:
        query.jurisdiction = _extract_jurisdiction(text)
    
    logger.info(
        f"Classification: {query_id} -> "
        f"type={query.query_type.value}, "
        f"jurisdiction={query.jurisdiction or 'None'}"
    )
    
    return {
        **state,
        "query": query,
    }


def _classify_query_type(text: str) -> QueryType:
    """
    Classify query type using keyword patterns.
    
    Order matters: Check specific patterns before generic ones.
    """
    
    # FACTUAL: Who, what, when, where, how much, how many
    factual_patterns = [
        r'\bwhat is (the|my|their|his|her)\b',
        r'\bwho is\b',
        r'\bwhen (is|was|does|did)\b',
        r'\bhow (much|many|long)\b',
        r'\blist (all|the)\b',
        r'\bname (the|all)\b',
        r'\bidentify\b',
    ]
    
    # PROCEDURAL: How to, steps, process, procedure
    procedural_patterns = [
        r'\bhow (do|can|should|to)\b',
        r'\bwhat (steps|process|procedure)\b',
        r'\bwhat.*required to\b',
        r'\bcan i\b',
        r'\bmay i\b',
        r'\bam i (allowed|required|obligated)\b',
    ]
    
    # COMPARATIVE: Compare, difference, better, versus
    comparative_patterns = [
        r'\b(compare|contrast|difference|versus|vs\.?)\b',
        r'\bbetter (than|to)\b',
        r'\bwhich is (better|stronger|weaker)\b',
        r'\binstead of\b',
        r'\balternative to\b',
    ]
    
    # INTERPRETIVE: Does this mean, apply, interpret, enforceable
    # (Default for most legal queries)
    interpretive_patterns = [
        r'\b(apply|applies|applicable)\b',
        r'\b(mean|means|meaning)\b',
        r'\b(interpret|interpretation)\b',
        r'\b(enforceable|valid|binding)\b',
        r'\bdoes (this|the|it)\b',
        r'\bis (this|the|it)\b',
        r'\bwould (this|the|it)\b',
        r'\bcover|include|protect\b',
    ]
    
    # Check procedural first (most specific)
    if any(re.search(pattern, text) for pattern in procedural_patterns):
        return QueryType.PROCEDURAL
    
    # Then comparative
    if any(re.search(pattern, text) for pattern in comparative_patterns):
        return QueryType.COMPARATIVE
    
    # Then factual
    if any(re.search(pattern, text) for pattern in factual_patterns):
        return QueryType.FACTUAL
    
    # Then interpretive
    if any(re.search(pattern, text) for pattern in interpretive_patterns):
        return QueryType.INTERPRETIVE
    
    # Default: If it's a question mark, assume interpretive
    # Otherwise factual (probably seeking specific info)
    if '?' in text:
        return QueryType.INTERPRETIVE
    else:
        return QueryType.FACTUAL


def _extract_jurisdiction(text: str) -> Optional[str]:
    """
    Extract jurisdiction mentions from query.
    
    Returns None if no clear jurisdiction found.
    """
    
    # US Federal patterns
    federal_patterns = [
        r'\bfederal\b',
        r'\bu\.?s\.?\s+(code|law|statute)\b',
        r'\bunited states\b',
        r'\bfisa\b',
        r'\bflsa\b',
        r'\bada\b',
        r'\btitle\s+\d+\b',
    ]
    
    # US State patterns (common ones)
    state_patterns = {
        'California': [r'\bcalifornia\b', r'\b\bCA\b'],
        'New York': [r'\bnew york\b', r'\bny\b'],
        'Texas': [r'\btexas\b', r'\btx\b'],
        'Florida': [r'\bflorida\b', r'\bfl\b'],
        'Illinois': [r'\billinois\b', r'\bil\b'],
        'Delaware': [r'\bdelaware\b', r'\bde\b'],
    }
    
    # Check federal
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in federal_patterns):
        return "US Federal"
    
    # Check states
    for state, patterns in state_patterns.items():
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
            return f"US - {state}"
    
    # Check for generic US
    if re.search(r'\b(us|u\.s\.)\b', text, re.IGNORECASE):
        return "US Federal"
    
    # No clear jurisdiction found
    return None

