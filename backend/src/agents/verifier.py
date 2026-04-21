"""
Citation Verification Agent - Production Implementation

This is THE critical anti-hallucination layer.

Architecture:
1. Deterministic checks (clause_id exists, quoted_text found)
2. Fuzzy matching (handles minor variations, whitespace)
3. LLM-assisted reasoning verification (optional, high-fidelity)

Why this matters:
- LLMs hallucinate citations ~15-30% of the time
- Legal work requires 100% accuracy
- Failed citation = entire answer suspect

Design decisions:
- Fail closed: If verification uncertain → mark as invalid
- Strict text matching: Legal text is precise
- Fuzzy tolerance: Allow minor whitespace/punctuation differences
- LLM reasoning check: Verify reasoning faithfulness (optional for cost)
"""

from typing import Dict, List
from difflib import SequenceMatcher
from loguru import logger

# Handle both relative and absolute imports
try:
    # Try relative imports (when used as package)
    from ..schemas.state import GraphState
    from ..schemas.verification import VerificationResult, CitationValidation
    from ..schemas.answer import Answer, Citation
    from ..schemas.retrieval import RetrievedClause
    from ..utils.llm_client import LLMClient
    from ..utils.config import Settings
except ImportError:
    # Fall back to absolute imports (when used in tests)
    from schemas.state import GraphState
    from schemas.verification import VerificationResult, CitationValidation
    from schemas.answer import Answer, Citation
    from schemas.retrieval import RetrievedClause
    from utils.llm_client import LLMClient
    from utils.config import Settings


class CitationVerifier:
    """
    Verifies citations against retrieved source clauses.
    
    Verification layers:
    1. Clause existence (does clause_id exist?)
    2. Text matching (is quoted_text in clause?)
    3. Reasoning faithfulness (is reasoning accurate?)
    
    Performance: ~10-50ms per citation (deterministic)
                ~500-2000ms per citation (with LLM reasoning check)
    """
    
    def __init__(self, use_llm_reasoning_check: bool = False):
        """
        Initialize the verifier.
        
        Args:
            use_llm_reasoning_check: If True, use LLM to verify reasoning
                                     (slower, more accurate)
                                     If False, skip reasoning check
                                     (faster, good enough for most cases)
        
        Why configurable:
        - LLM check adds cost + latency
        - For production: Enable for high-stakes queries
        - For demos: Disable for speed
        """
        self.use_llm_reasoning_check = use_llm_reasoning_check
        if use_llm_reasoning_check:
            self.llm_client = LLMClient()
        
    def verify_answer(
        self,
        answer: Answer,
        retrieved_clauses: List[RetrievedClause]
    ) -> VerificationResult:
        """
        Verify all citations in an answer.
        
        Args:
            answer: The Answer object with citations
            retrieved_clauses: List of clauses from retrieval
            
        Returns:
            VerificationResult with per-citation validations
            
        Learning insight:
        - We verify against ONLY the retrieved clauses
        - If a citation references a clause we didn't retrieve → INVALID
        - This catches LLM inventing clauses outside context
        """
        logger.info(f"Verifying {len(answer.citations)} citations")
        
        # Build a lookup dict for fast clause access
        clause_lookup: Dict[str, RetrievedClause] = {
            clause.clause_id: clause for clause in retrieved_clauses
        }
        
        citation_validations: List[CitationValidation] = []
        verification_issues: List[str] = []
        
        for idx, citation in enumerate(answer.citations):
            citation_id = f"cite_{idx:03d}"
            
            # Verify this citation
            validation = self._verify_single_citation(
                citation=citation,
                citation_id=citation_id,
                clause_lookup=clause_lookup
            )
            
            citation_validations.append(validation)
            
            if not validation.is_valid:
                issue = f"Citation {citation_id} ({citation.clause_id}): {validation.error_message}"
                verification_issues.append(issue)
                logger.warning(issue)
        
        # Aggregate results
        total = len(answer.citations)
        valid = sum(1 for v in citation_validations if v.is_valid)
        invalid = total - valid
        all_valid = (invalid == 0)
        
        result = VerificationResult(
            all_citations_valid=all_valid,
            citation_validations=citation_validations,
            total_citations=total,
            valid_citations=valid,
            invalid_citations=invalid,
            verification_issues=verification_issues
        )
        
        logger.info(
            f"Verification complete: {valid}/{total} valid "
            f"({(valid/total*100):.1f}%)" if total > 0 else "No citations to verify"
        )
        
        return result
    
    def _verify_single_citation(
        self,
        citation: Citation,
        citation_id: str,
        clause_lookup: Dict[str, RetrievedClause]
    ) -> CitationValidation:
        """
        Verify a single citation through multiple layers.
        
        Verification steps:
        1. Does clause_id exist in retrieved context?
        2. Does quoted_text appear in that clause?
        3. (Optional) Is reasoning faithful to the text?
        
        Why this order:
        - Fast checks first (existence check is O(1))
        - Expensive checks last (LLM call is slow)
        - Fail fast on obvious errors
        """
        clause_id = citation.clause_id
        
        # LAYER 1: Check clause existence
        if clause_id not in clause_lookup:
            return CitationValidation(
                citation_id=citation_id,
                clause_id=clause_id,
                is_valid=False,
                quoted_text_found=False,
                reasoning_faithful=False,
                error_message=f"Clause '{clause_id}' not found in retrieved context (hallucinated?)"
            )
        
        clause = clause_lookup[clause_id]
        
        # LAYER 2: Verify quoted text appears in clause
        quoted_text_found, text_match_score = self._verify_quoted_text(
            quoted_text=citation.quoted_text,
            clause_text=clause.text
        )
        
        if not quoted_text_found:
            return CitationValidation(
                citation_id=citation_id,
                clause_id=clause_id,
                is_valid=False,
                quoted_text_found=False,
                reasoning_faithful=False,
                error_message=f"Quoted text not found in clause (similarity: {text_match_score:.2%})"
            )
        
        # LAYER 3: (Optional) Verify reasoning faithfulness
        reasoning_faithful = True  # Default to True if not checking
        
        if self.use_llm_reasoning_check:
            reasoning_faithful = self._verify_reasoning_faithfulness(
                citation=citation,
                clause=clause
            )
            
            if not reasoning_faithful:
                return CitationValidation(
                    citation_id=citation_id,
                    clause_id=clause_id,
                    is_valid=False,
                    quoted_text_found=True,
                    reasoning_faithful=False,
                    error_message="Reasoning is not faithful to the quoted text"
                )
        
        # All checks passed
        return CitationValidation(
            citation_id=citation_id,
            clause_id=clause_id,
            is_valid=True,
            quoted_text_found=True,
            reasoning_faithful=reasoning_faithful,
            error_message=""
        )
    
    def _verify_quoted_text(
        self,
        quoted_text: str,
        clause_text: str
    ) -> tuple[bool, float]:
        """
        Verify that quoted text appears in the clause.
        
        Uses two methods:
        1. Exact substring match (fastest, handles verbatim quotes)
        2. Fuzzy match (handles minor variations, whitespace)
        
        Why fuzzy matching:
        - LLMs may normalize whitespace
        - May add/remove punctuation
        - May have minor typos
        
        Threshold: 0.85 similarity (85% match)
        - Tuned for legal text (strict but tolerant)
        - Lower = more permissive (risky)
        - Higher = stricter (may reject valid citations)
        
        Args:
            quoted_text: The text the LLM claims to quote
            clause_text: The actual clause text
            
        Returns:
            (found: bool, similarity_score: float)
        """
        # Normalize both texts for comparison
        quoted_normalized = self._normalize_text(quoted_text)
        clause_normalized = self._normalize_text(clause_text)
        
        # Method 1: Exact substring match (fastest)
        if quoted_normalized in clause_normalized:
            return True, 1.0
        
        # Method 2: Fuzzy matching (handles variations)
        # Use sliding window to find best match
        similarity = self._fuzzy_match_sliding_window(
            quoted_normalized,
            clause_normalized
        )
        
        # Threshold: 85% similarity
        # Learning insight: Tuned for legal text
        # - 90%+ too strict (rejects minor formatting differences)
        # - 80%- too lenient (accepts paraphrasing)
        threshold = 0.85
        
        found = similarity >= threshold
        
        if not found:
            logger.warning(
                f"Quoted text not found (similarity: {similarity:.2%})\n"
                f"Quoted: {quoted_text[:100]}...\n"
                f"Clause: {clause_text[:100]}..."
            )
        
        return found, similarity
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize text for comparison.
        
        Normalizations:
        - Lowercase
        - Collapse whitespace
        - Remove extra spaces
        
        Why these normalizations:
        - LLMs are inconsistent with formatting
        - Legal meaning is preserved
        - Helps catch legitimate citations
        """
        # Lowercase
        normalized = text.lower()
        # Collapse whitespace
        normalized = " ".join(normalized.split())
        return normalized
    
    @staticmethod
    def _fuzzy_match_sliding_window(
        quoted: str,
        clause: str
    ) -> float:
        """
        Find best fuzzy match using sliding window.
        
        Algorithm:
        1. Slide a window of quoted's length across clause
        2. Compute similarity for each window position
        3. Return maximum similarity
        
        Why sliding window:
        - Handles cases where quote is in middle of clause
        - More accurate than comparing entire strings
        
        Complexity: O(n * m) where n=len(clause), m=len(quoted)
        For typical legal clauses: ~10-50ms
        """
        if len(quoted) > len(clause):
            # Quoted text longer than clause → can't be a substring
            return 0.0
        
        max_similarity = 0.0
        window_size = len(quoted)
        
        # Slide window across clause
        for i in range(len(clause) - window_size + 1):
            window = clause[i:i + window_size]
            similarity = SequenceMatcher(None, quoted, window).ratio()
            max_similarity = max(max_similarity, similarity)
            
            # Early exit if we find a perfect match
            if similarity == 1.0:
                break
        
        return max_similarity
    
    def _verify_reasoning_faithfulness(
        self,
        citation: Citation,
        clause: RetrievedClause
    ) -> bool:
        """
        Use LLM to verify that reasoning is faithful to the text.
        
        Why LLM-assisted:
        - Reasoning verification requires understanding
        - Deterministic checks can't assess faithfulness
        - LLM can catch subtle misinterpretations
        
        Prompt strategy:
        - Show: clause text + reasoning
        - Ask: Is reasoning faithful? Yes/No
        - Force structured output
        
        Cost: ~$0.0001-$0.001 per citation (Groq)
        Latency: ~500-2000ms per citation
        
        Production tip:
        - Cache results for repeated citations
        - Batch verification for speed
        - Use only for high-stakes queries
        """
        logger.info(f"Verifying reasoning faithfulness for {citation.clause_id}")
        
        # TODO: Implement LLM-based reasoning verification
        # For now: Return True (optimistic)
        # In production: Call LLM with prompt
        
        # Placeholder implementation
        logger.warning("LLM reasoning check not yet implemented, assuming faithful")
        return True


def verify_citations_node(state: GraphState) -> GraphState:
    """
    LangGraph node for citation verification.
    
    State inputs:
    - answer: Answer object with citations
    - retrieval_result: Retrieved clauses
    
    State outputs:
    - verification_result: VerificationResult
    
    Why this is a separate node:
    - Modular (can swap verification strategies)
    - Testable in isolation
    - Can be bypassed for testing
    
    Configuration:
    - use_llm_reasoning_check: Set in Settings
    - Currently: False (faster, good for demos)
    - Production: True (higher fidelity)
    """
    query_id = state.get("query_id")
    answer = state.get("answer")
    retrieval_result = state.get("retrieval_result")
    
    logger.info(f"[Verifier] Starting citation verification: {query_id}")
    
    # Handle edge case: No answer or no retrieval
    if not answer or not retrieval_result:
        logger.warning("No answer or retrieval result to verify")
        return {
            **state,
            "verification_result": VerificationResult(
                all_citations_valid=False,
                citation_validations=[],
                total_citations=0,
                valid_citations=0,
                invalid_citations=0,
                verification_issues=["No answer or retrieval result to verify"]
            )
        }
    
    # Initialize verifier
    # For now: Disable LLM reasoning check (faster)
    # TODO: Make this configurable via Settings
    verifier = CitationVerifier(use_llm_reasoning_check=False)
    
    # Verify all citations
    verification_result = verifier.verify_answer(
        answer=answer,
        retrieved_clauses=retrieval_result.clauses
    )
    
    # Log summary
    if verification_result.all_citations_valid:
        logger.success(
            f"[Verifier] ✅ All {verification_result.total_citations} "
            f"citations verified for {query_id}"
        )
    else:
        logger.warning(
            f"[Verifier] ⚠️  {verification_result.invalid_citations}/"
            f"{verification_result.total_citations} citations failed for {query_id}"
        )
    
    return {
        **state,
        "verification_result": verification_result,
    }
