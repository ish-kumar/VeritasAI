"""
Test Citation Verifier - Comprehensive Test Suite

This script tests the Citation Verifier's ability to catch:
1. Valid citations (should pass)
2. Hallucinated clause IDs (should fail)
3. Misquoted text / paraphrasing (should fail)
4. Minor formatting variations (should pass with fuzzy matching)

Learning goals:
- See how fuzzy matching handles whitespace/formatting
- Understand what constitutes a "valid" citation
- See the verifier catch LLM hallucinations
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent / "src"
sys.path.insert(0, str(backend_src))

from loguru import logger

# Import schemas first
from schemas.answer import Answer, Citation
from schemas.retrieval import RetrievedClause

# Import verifier directly to avoid relative import issues
from agents.verifier import CitationVerifier


def test_valid_citations():
    """
    Test Case 1: All citations are valid.
    
    Expected result: All pass verification
    """
    print("\n" + "="*80)
    print("TEST 1: Valid Citations (Should Pass)")
    print("="*80)
    
    # Mock retrieved clauses
    retrieved_clauses = [
        RetrievedClause(
            clause_id="DOC1_SEC5.2",
            text="The Employee agrees not to disclose any Confidential Information to third parties without prior written consent from the Employer. This obligation survives termination of employment.",
            document_id="DOC1",
            section="Section 5.2 - Confidentiality",
            similarity_score=0.92,
            metadata={"jurisdiction": "California"}
        ),
        RetrievedClause(
            clause_id="DOC1_SEC12.3",
            text="Any dispute arising under this Agreement shall be resolved through binding arbitration in accordance with the rules of the American Arbitration Association.",
            document_id="DOC1",
            section="Section 12.3 - Dispute Resolution",
            similarity_score=0.88,
            metadata={"jurisdiction": "California"}
        ),
    ]
    
    # Mock answer with valid citations
    answer = Answer(
        answer_text="Yes, the employee is prohibited from sharing confidential information with third parties, and disputes must be resolved through arbitration.",
        citations=[
            Citation(
                clause_id="DOC1_SEC5.2",
                quoted_text="The Employee agrees not to disclose any Confidential Information to third parties without prior written consent",
                reasoning="This clause explicitly prohibits disclosure of confidential information"
            ),
            Citation(
                clause_id="DOC1_SEC12.3",
                quoted_text="Any dispute arising under this Agreement shall be resolved through binding arbitration",
                reasoning="This clause mandates arbitration for all disputes"
            ),
        ],
        reasoning="Based on the confidentiality and dispute resolution clauses",
        assumptions=["Agreement is valid and enforceable"],
        caveats=["Certain statutory claims may be exempt from arbitration"]
    )
    
    # Verify
    verifier = CitationVerifier(use_llm_reasoning_check=False)
    result = verifier.verify_answer(answer, retrieved_clauses)
    
    # Print results
    print(f"\n✅ Result: {result.valid_citations}/{result.total_citations} citations valid")
    print(f"All valid: {result.all_citations_valid}")
    
    for validation in result.citation_validations:
        status = "✅ PASS" if validation.is_valid else "❌ FAIL"
        print(f"\n{status} - Citation: {validation.clause_id}")
        print(f"  Quoted text found: {validation.quoted_text_found}")
        print(f"  Reasoning faithful: {validation.reasoning_faithful}")
        if validation.error_message:
            print(f"  Error: {validation.error_message}")
    
    assert result.all_citations_valid, "Expected all citations to be valid"
    print("\n✅ Test 1 PASSED")


def test_hallucinated_clause_id():
    """
    Test Case 2: LLM invents a clause ID that doesn't exist.
    
    This is a common hallucination pattern:
    - LLM generates plausible-looking clause_id
    - But it's not in the retrieved context
    
    Expected result: Verification fails
    """
    print("\n" + "="*80)
    print("TEST 2: Hallucinated Clause ID (Should Fail)")
    print("="*80)
    
    # Mock retrieved clauses (only one clause)
    retrieved_clauses = [
        RetrievedClause(
            clause_id="DOC1_SEC5.2",
            text="The Employee agrees not to disclose any Confidential Information.",
            document_id="DOC1",
            section="Section 5.2",
            similarity_score=0.92,
            metadata={}
        ),
    ]
    
    # Mock answer citing a clause that DOESN'T exist
    answer = Answer(
        answer_text="The employee must provide 30 days notice before termination.",
        citations=[
            Citation(
                clause_id="DOC1_SEC8.5",  # ❌ This clause doesn't exist!
                quoted_text="Employee must provide 30 days written notice",
                reasoning="This clause specifies the notice period"
            ),
        ],
        reasoning="Based on the termination notice clause",
        assumptions=[],
        caveats=[]
    )
    
    # Verify
    verifier = CitationVerifier(use_llm_reasoning_check=False)
    result = verifier.verify_answer(answer, retrieved_clauses)
    
    # Print results
    print(f"\n❌ Result: {result.valid_citations}/{result.total_citations} citations valid")
    print(f"All valid: {result.all_citations_valid}")
    
    for validation in result.citation_validations:
        status = "✅ PASS" if validation.is_valid else "❌ FAIL"
        print(f"\n{status} - Citation: {validation.clause_id}")
        print(f"  Error: {validation.error_message}")
    
    assert not result.all_citations_valid, "Expected verification to fail"
    assert "not found in retrieved context" in result.citation_validations[0].error_message
    print("\n✅ Test 2 PASSED (correctly caught hallucination)")


def test_misquoted_text():
    """
    Test Case 3: LLM paraphrases instead of quoting verbatim.
    
    This is another common failure mode:
    - clause_id is correct
    - But quoted_text is paraphrased/summarized
    
    Why this matters:
    - Legal text is precise
    - Paraphrasing can change meaning
    - We need verbatim quotes
    
    Expected result: Verification fails (similarity < 85%)
    """
    print("\n" + "="*80)
    print("TEST 3: Misquoted Text / Paraphrasing (Should Fail)")
    print("="*80)
    
    # Mock retrieved clauses
    retrieved_clauses = [
        RetrievedClause(
            clause_id="DOC1_SEC5.2",
            text="The Employee agrees not to disclose any Confidential Information to third parties without prior written consent from the Employer.",
            document_id="DOC1",
            section="Section 5.2",
            similarity_score=0.92,
            metadata={}
        ),
    ]
    
    # Mock answer with paraphrased text (not verbatim)
    answer = Answer(
        answer_text="Employees cannot share confidential information.",
        citations=[
            Citation(
                clause_id="DOC1_SEC5.2",  # ✅ Clause ID is correct
                quoted_text="Employees must keep confidential information secret and not share it with anyone.",  # ❌ Paraphrased!
                reasoning="This clause requires confidentiality"
            ),
        ],
        reasoning="Based on confidentiality obligations",
        assumptions=[],
        caveats=[]
    )
    
    # Verify
    verifier = CitationVerifier(use_llm_reasoning_check=False)
    result = verifier.verify_answer(answer, retrieved_clauses)
    
    # Print results
    print(f"\n❌ Result: {result.valid_citations}/{result.total_citations} citations valid")
    print(f"All valid: {result.all_citations_valid}")
    
    for validation in result.citation_validations:
        status = "✅ PASS" if validation.is_valid else "❌ FAIL"
        print(f"\n{status} - Citation: {validation.clause_id}")
        print(f"  Quoted text found: {validation.quoted_text_found}")
        if validation.error_message:
            print(f"  Error: {validation.error_message}")
    
    assert not result.all_citations_valid, "Expected verification to fail"
    assert not result.citation_validations[0].quoted_text_found
    print("\n✅ Test 3 PASSED (correctly caught paraphrasing)")


def test_fuzzy_matching():
    """
    Test Case 4: Minor formatting variations (should pass with fuzzy matching).
    
    This tests the fuzzy matching tolerance:
    - Extra whitespace
    - Different capitalization
    - Minor punctuation differences
    
    Expected result: Pass (similarity > 85%)
    """
    print("\n" + "="*80)
    print("TEST 4: Fuzzy Matching (Minor Variations - Should Pass)")
    print("="*80)
    
    # Mock retrieved clauses
    retrieved_clauses = [
        RetrievedClause(
            clause_id="DOC1_SEC5.2",
            text="The Employee agrees not to disclose any Confidential Information to third parties without prior written consent from the Employer.",
            document_id="DOC1",
            section="Section 5.2",
            similarity_score=0.92,
            metadata={}
        ),
    ]
    
    # Mock answer with minor formatting differences
    answer = Answer(
        answer_text="Employees cannot share confidential information.",
        citations=[
            Citation(
                clause_id="DOC1_SEC5.2",
                # Minor differences: extra spaces, different capitalization
                quoted_text="the  employee agrees not to disclose any confidential information to third parties",
                reasoning="This clause prohibits disclosure"
            ),
        ],
        reasoning="Based on confidentiality obligations",
        assumptions=[],
        caveats=[]
    )
    
    # Verify
    verifier = CitationVerifier(use_llm_reasoning_check=False)
    result = verifier.verify_answer(answer, retrieved_clauses)
    
    # Print results
    print(f"\n✅ Result: {result.valid_citations}/{result.total_citations} citations valid")
    print(f"All valid: {result.all_citations_valid}")
    
    for validation in result.citation_validations:
        status = "✅ PASS" if validation.is_valid else "❌ FAIL"
        print(f"\n{status} - Citation: {validation.clause_id}")
        print(f"  Quoted text found: {validation.quoted_text_found}")
    
    assert result.all_citations_valid, "Expected fuzzy matching to pass"
    print("\n✅ Test 4 PASSED (fuzzy matching works)")


def test_mixed_results():
    """
    Test Case 5: Mix of valid and invalid citations.
    
    Real-world scenario:
    - Some citations are correct
    - Some are hallucinated
    
    Expected result: Overall verification fails (not all valid)
    """
    print("\n" + "="*80)
    print("TEST 5: Mixed Results (Some Valid, Some Invalid)")
    print("="*80)
    
    # Mock retrieved clauses
    retrieved_clauses = [
        RetrievedClause(
            clause_id="DOC1_SEC5.2",
            text="The Employee agrees not to disclose any Confidential Information.",
            document_id="DOC1",
            section="Section 5.2",
            similarity_score=0.92,
            metadata={}
        ),
    ]
    
    # Mock answer with mixed citations
    answer = Answer(
        answer_text="Employees must maintain confidentiality and provide 30 days notice.",
        citations=[
            # ✅ Valid citation
            Citation(
                clause_id="DOC1_SEC5.2",
                quoted_text="The Employee agrees not to disclose any Confidential Information",
                reasoning="This clause requires confidentiality"
            ),
            # ❌ Hallucinated clause
            Citation(
                clause_id="DOC1_SEC8.5",  # Doesn't exist
                quoted_text="30 days written notice required",
                reasoning="This clause specifies notice period"
            ),
        ],
        reasoning="Based on multiple clauses",
        assumptions=[],
        caveats=[]
    )
    
    # Verify
    verifier = CitationVerifier(use_llm_reasoning_check=False)
    result = verifier.verify_answer(answer, retrieved_clauses)
    
    # Print results
    print(f"\n⚠️  Result: {result.valid_citations}/{result.total_citations} citations valid")
    print(f"All valid: {result.all_citations_valid}")
    
    for validation in result.citation_validations:
        status = "✅ PASS" if validation.is_valid else "❌ FAIL"
        print(f"\n{status} - Citation: {validation.clause_id}")
        if validation.error_message:
            print(f"  Error: {validation.error_message}")
    
    assert not result.all_citations_valid, "Expected overall verification to fail"
    assert result.valid_citations == 1, "Expected 1 valid citation"
    assert result.invalid_citations == 1, "Expected 1 invalid citation"
    print("\n✅ Test 5 PASSED (correctly identified mixed results)")


def main():
    """Run all verification tests."""
    logger.remove()  # Remove default logger
    logger.add(sys.stderr, level="INFO")
    
    print("\n" + "="*80)
    print("CITATION VERIFICATION TEST SUITE")
    print("="*80)
    print("\nThis test suite demonstrates the Citation Verifier's ability to:")
    print("1. Validate correct citations")
    print("2. Catch hallucinated clause IDs")
    print("3. Detect paraphrased/misquoted text")
    print("4. Handle minor formatting variations (fuzzy matching)")
    print("5. Handle mixed valid/invalid citations")
    
    try:
        test_valid_citations()
        test_hallucinated_clause_id()
        test_misquoted_text()
        test_fuzzy_matching()
        test_mixed_results()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        print("\n🎓 Key Takeaways:")
        print("1. Verifier catches hallucinated clause IDs (LLM invents sources)")
        print("2. Verifier detects paraphrasing (requires verbatim quotes)")
        print("3. Fuzzy matching handles minor formatting (85% similarity threshold)")
        print("4. Single failed citation → entire answer marked suspect")
        print("\n🚀 This is production-ready anti-hallucination protection!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Test error")
        sys.exit(1)


if __name__ == "__main__":
    main()
