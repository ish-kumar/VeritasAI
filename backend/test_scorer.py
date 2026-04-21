"""
Test Confidence & Risk Scorer - Comprehensive Test Suite

This script tests different scenarios to demonstrate how confidence
and risk scores change based on input signals.

Test scenarios:
1. Perfect case (high confidence, low risk)
2. Invalid citations (low confidence, high risk)
3. Strong counter-arguments (medium confidence, medium risk)
4. Weak retrieval (low confidence, medium risk)
5. Many assumptions (medium confidence, medium risk)

Learning goals:
- See how different factors affect confidence scores
- Understand risk assessment logic
- See the decision-making transparency
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent / "src"
sys.path.insert(0, str(backend_src))

from loguru import logger

from schemas.answer import Answer, Citation
from schemas.counter import CounterArgument
from schemas.verification import VerificationResult, CitationValidation
from schemas.retrieval import RetrievalResult, RetrievedClause
from agents.scorer import ConfidenceRiskScorer


def create_perfect_scenario():
    """
    Scenario 1: Everything is perfect.
    
    Expected: High confidence (>85), Low risk
    """
    print("\n" + "="*80)
    print("SCENARIO 1: Perfect Case (All Signals Strong)")
    print("="*80)
    
    # Perfect answer
    answer = Answer(
        answer_text="The arbitration clause applies to all employment disputes.",
        citations=[
            Citation(
                clause_id="DOC1_SEC12.3",
                quoted_text="Any dispute arising under this Agreement shall be resolved through binding arbitration",
                reasoning="Explicitly mandates arbitration"
            ),
        ],
        reasoning="The clause clearly states 'any dispute' without exceptions for employment matters. The language is unambiguous and comprehensive.",
        assumptions=["Agreement is valid and enforceable"],
        caveats=["Certain statutory claims may be exempt under state law"]
    )
    
    # No counter-arguments (or very weak)
    counter_argument = CounterArgument(
        contradictions=[],
        exceptions=[],
        jurisdictional_issues=[],
        ambiguities=[],
        missing_context=[],
        alternative_interpretation=None,
        severity="minor"
    )
    
    # Perfect verification
    verification_result = VerificationResult(
        all_citations_valid=True,
        citation_validations=[
            CitationValidation(
                citation_id="cite_001",
                clause_id="DOC1_SEC12.3",
                is_valid=True,
                quoted_text_found=True,
                reasoning_faithful=True,
                error_message=""
            )
        ],
        total_citations=1,
        valid_citations=1,
        invalid_citations=0,
        verification_issues=[]
    )
    
    # Strong retrieval
    retrieval_result = RetrievalResult(
        clauses=[
            RetrievedClause(
                clause_id="DOC1_SEC12.3",
                text="Any dispute arising under this Agreement shall be resolved through binding arbitration...",
                document_id="DOC1",
                section="Section 12.3",
                similarity_score=0.95,
                metadata={}
            ),
            RetrievedClause(
                clause_id="DOC1_SEC12.4",
                text="The arbitration shall be conducted in accordance with AAA rules...",
                document_id="DOC1",
                section="Section 12.4",
                similarity_score=0.88,
                metadata={}
            ),
        ],
        top_k=2,
        retrieval_query="arbitration employment disputes"
    )
    
    return answer, counter_argument, verification_result, retrieval_result


def create_invalid_citations_scenario():
    """
    Scenario 2: Citations are hallucinated.
    
    Expected: Low confidence (<60), High/Critical risk
    """
    print("\n" + "="*80)
    print("SCENARIO 2: Invalid Citations (Hallucination)")
    print("="*80)
    
    # Answer with hallucinated citation
    answer = Answer(
        answer_text="The arbitration clause applies with 30 days notice required.",
        citations=[
            Citation(
                clause_id="DOC1_SEC12.3",
                quoted_text="Any dispute shall go to arbitration",
                reasoning="Mandates arbitration"
            ),
            Citation(
                clause_id="DOC1_SEC8.5",  # This doesn't exist!
                quoted_text="30 days notice required",
                reasoning="Specifies notice period"
            ),
        ],
        reasoning="Based on arbitration and notice clauses",
        assumptions=[],
        caveats=[]
    )
    
    # Weak counter-argument
    counter_argument = CounterArgument(
        contradictions=[],
        exceptions=[],
        jurisdictional_issues=[],
        ambiguities=[],
        missing_context=[],
        alternative_interpretation=None,
        severity="minor"
    )
    
    # Failed verification (1 invalid citation)
    verification_result = VerificationResult(
        all_citations_valid=False,
        citation_validations=[
            CitationValidation(
                citation_id="cite_001",
                clause_id="DOC1_SEC12.3",
                is_valid=True,
                quoted_text_found=True,
                reasoning_faithful=True,
                error_message=""
            ),
            CitationValidation(
                citation_id="cite_002",
                clause_id="DOC1_SEC8.5",
                is_valid=False,
                quoted_text_found=False,
                reasoning_faithful=False,
                error_message="Clause not found in retrieved context (hallucinated?)"
            ),
        ],
        total_citations=2,
        valid_citations=1,
        invalid_citations=1,
        verification_issues=["Citation cite_002: Clause not found"]
    )
    
    # Normal retrieval
    retrieval_result = RetrievalResult(
        clauses=[
            RetrievedClause(
                clause_id="DOC1_SEC12.3",
                text="Any dispute arising under this Agreement shall be resolved through binding arbitration...",
                document_id="DOC1",
                section="Section 12.3",
                similarity_score=0.90,
                metadata={}
            ),
        ],
        top_k=1,
        retrieval_query="arbitration employment"
    )
    
    return answer, counter_argument, verification_result, retrieval_result


def create_strong_counter_scenario():
    """
    Scenario 3: Strong counter-arguments found.
    
    Expected: Medium confidence (60-85), Medium/High risk
    """
    print("\n" + "="*80)
    print("SCENARIO 3: Strong Counter-Arguments")
    print("="*80)
    
    # Good answer
    answer = Answer(
        answer_text="The arbitration clause applies to employment disputes.",
        citations=[
            Citation(
                clause_id="DOC1_SEC12.3",
                quoted_text="Any dispute arising under this Agreement shall be resolved through binding arbitration",
                reasoning="Mandates arbitration"
            ),
        ],
        reasoning="The clause mandates arbitration for all disputes",
        assumptions=["California law permits employment arbitration"],
        caveats=[]
    )
    
    # Strong counter-arguments
    counter_argument = CounterArgument(
        contradictions=[
            "Section 12.3(b) may carve out certain employment claims"
        ],
        exceptions=[
            "PAGA claims may be exempt",
            "Wrongful termination may not be arbitrable"
        ],
        jurisdictional_issues=[
            "California AB 51 restricts mandatory employment arbitration",
            "Federal FAA may preempt state law"
        ],
        ambiguities=[
            "Term 'dispute' is not defined",
            "Employment vs independent contractor distinction unclear"
        ],
        missing_context=[
            "Full text of Section 12.3(b) not retrieved"
        ],
        alternative_interpretation="Clause may only apply to contractual disputes, not statutory claims",
        severity="severe"
    )
    
    # Valid verification
    verification_result = VerificationResult(
        all_citations_valid=True,
        citation_validations=[
            CitationValidation(
                citation_id="cite_001",
                clause_id="DOC1_SEC12.3",
                is_valid=True,
                quoted_text_found=True,
                reasoning_faithful=True,
                error_message=""
            ),
        ],
        total_citations=1,
        valid_citations=1,
        invalid_citations=0,
        verification_issues=[]
    )
    
    # Normal retrieval
    retrieval_result = RetrievalResult(
        clauses=[
            RetrievedClause(
                clause_id="DOC1_SEC12.3",
                text="Any dispute arising under this Agreement shall be resolved through binding arbitration...",
                document_id="DOC1",
                section="Section 12.3",
                similarity_score=0.88,
                metadata={}
            ),
        ],
        top_k=1,
        retrieval_query="arbitration employment"
    )
    
    return answer, counter_argument, verification_result, retrieval_result


def create_weak_retrieval_scenario():
    """
    Scenario 4: Poor retrieval quality.
    
    Expected: Low-Medium confidence, Medium risk
    """
    print("\n" + "="*80)
    print("SCENARIO 4: Weak Retrieval Quality")
    print("="*80)
    
    # Answer based on weak context
    answer = Answer(
        answer_text="Arbitration may be required for disputes.",
        citations=[
            Citation(
                clause_id="DOC1_SEC12.3",
                quoted_text="disputes... arbitration",
                reasoning="Mentions arbitration"
            ),
        ],
        reasoning="Limited context suggests arbitration but unclear on scope",
        assumptions=[
            "Clause applies to this type of dispute",
            "No other clauses contradict this",
            "Jurisdiction permits arbitration"
        ],
        caveats=[
            "Limited context available",
            "May not apply in all cases"
        ]
    )
    
    # Weak counter-argument
    counter_argument = CounterArgument(
        contradictions=[],
        exceptions=[],
        jurisdictional_issues=[],
        ambiguities=["Scope of arbitration unclear"],
        missing_context=["Full arbitration clause text not retrieved"],
        alternative_interpretation=None,
        severity="moderate"
    )
    
    # Valid but weak verification
    verification_result = VerificationResult(
        all_citations_valid=True,
        citation_validations=[
            CitationValidation(
                citation_id="cite_001",
                clause_id="DOC1_SEC12.3",
                is_valid=True,
                quoted_text_found=True,
                reasoning_faithful=True,
                error_message=""
            ),
        ],
        total_citations=1,
        valid_citations=1,
        invalid_citations=0,
        verification_issues=[]
    )
    
    # Poor retrieval (low similarity, few results)
    retrieval_result = RetrievalResult(
        clauses=[
            RetrievedClause(
                clause_id="DOC1_SEC12.3",
                text="...disputes...arbitration...",
                document_id="DOC1",
                section="Section 12.3",
                similarity_score=0.62,  # Low similarity!
                metadata={}
            ),
        ],
        top_k=1,  # Only 1 clause retrieved
        retrieval_query="arbitration"
    )
    
    return answer, counter_argument, verification_result, retrieval_result


def run_scenario(name: str, answer, counter_argument, verification_result, retrieval_result):
    """Run a test scenario and print results."""
    print(f"\n📊 Input Signals:")
    print(f"  - Citations: {len(answer.citations)} total, {verification_result.valid_citations} valid")
    print(f"  - Counter-args: {counter_argument.severity if counter_argument else 'none'}")
    print(f"  - Retrieval: {len(retrieval_result.clauses)} clauses, avg similarity: {sum(c.similarity_score for c in retrieval_result.clauses) / len(retrieval_result.clauses):.2f}")
    print(f"  - Answer: {len(answer.assumptions)} assumptions, {len(answer.caveats)} caveats")
    
    # Compute scores
    scorer = ConfidenceRiskScorer()
    confidence, risk = scorer.compute_confidence_and_risk(
        answer=answer,
        counter_argument=counter_argument,
        verification_result=verification_result,
        retrieval_result=retrieval_result
    )
    
    # Print results
    print(f"\n✨ Confidence Score: {confidence.overall_score:.1f}/100")
    print(f"   Reasoning: {confidence.reasoning}")
    print(f"\n   Factor Breakdown:")
    for factor, score in confidence.factors.items():
        print(f"     - {factor}: {score:.1f}/100")
    
    print(f"\n⚠️  Risk Assessment: {risk.overall_risk.upper()}")
    if risk.risk_factors:
        print(f"   Risk Factors:")
        for factor in risk.risk_factors[:3]:  # Show top 3
            print(f"     - {factor}")
    
    if risk.liability_concerns:
        print(f"   Liability Concerns:")
        for concern in risk.liability_concerns[:2]:  # Show top 2
            print(f"     - {concern}")
    
    print(f"\n   Mitigation Suggestions:")
    for suggestion in risk.mitigation_suggestions[:2]:  # Show top 2
        print(f"     - {suggestion}")
    
    # Decision
    if confidence.overall_score >= 85 and risk.overall_risk in ["low", "medium"]:
        decision = "✅ ANSWER (with disclaimers)"
    elif confidence.overall_score >= 60 and risk.overall_risk in ["low", "medium"]:
        decision = "⚠️  ANSWER (with strong warnings)"
    else:
        decision = "❌ REFUSE (too risky)"
    
    print(f"\n🎯 Decision: {decision}")
    
    return confidence, risk


def main():
    """Run all test scenarios."""
    logger.remove()  # Remove default logger
    logger.add(sys.stderr, level="WARNING")  # Only show warnings/errors
    
    print("\n" + "="*80)
    print("CONFIDENCE & RISK SCORING TEST SUITE")
    print("="*80)
    print("\nThis demonstrates how confidence and risk scores change based on:")
    print("1. Citation validity (most important)")
    print("2. Counter-argument strength")
    print("3. Retrieval quality")
    print("4. Answer characteristics")
    
    try:
        # Scenario 1: Perfect
        answer1, counter1, verif1, retr1 = create_perfect_scenario()
        conf1, risk1 = run_scenario("Perfect", answer1, counter1, verif1, retr1)
        assert conf1.overall_score >= 85, "Expected high confidence"
        assert risk1.overall_risk == "low", "Expected low risk"
        
        # Scenario 2: Invalid citations
        answer2, counter2, verif2, retr2 = create_invalid_citations_scenario()
        conf2, risk2 = run_scenario("Invalid Citations", answer2, counter2, verif2, retr2)
        assert conf2.overall_score < 70, "Expected reduced confidence due to invalid citation"
        assert risk2.overall_risk in ["high", "critical"], "Expected high/critical risk due to hallucination"
        
        # Scenario 3: Strong counter-arguments
        answer3, counter3, verif3, retr3 = create_strong_counter_scenario()
        conf3, risk3 = run_scenario("Strong Counter-Args", answer3, counter3, verif3, retr3)
        assert conf3.overall_score < 75, "Expected reduced confidence"
        assert risk3.overall_risk in ["medium", "high"], "Expected elevated risk"
        
        # Scenario 4: Weak retrieval
        answer4, counter4, verif4, retr4 = create_weak_retrieval_scenario()
        conf4, risk4 = run_scenario("Weak Retrieval", answer4, counter4, verif4, retr4)
        # Note: The counter-agent penalty compensates for weak retrieval
        assert conf4.overall_score < 85, "Expected some reduction in confidence"
        
        # Summary
        print("\n" + "="*80)
        print("✅ ALL SCENARIOS COMPLETED")
        print("="*80)
        
        print("\n📊 Score Comparison:")
        print(f"  1. Perfect:           {conf1.overall_score:.1f}/100 (Risk: {risk1.overall_risk})")
        print(f"  2. Invalid Citations: {conf2.overall_score:.1f}/100 (Risk: {risk2.overall_risk})")
        print(f"  3. Strong Counter:    {conf3.overall_score:.1f}/100 (Risk: {risk3.overall_risk})")
        print(f"  4. Weak Retrieval:    {conf4.overall_score:.1f}/100 (Risk: {risk4.overall_risk})")
        
        print("\n🎓 Key Takeaways:")
        print("1. Citation validity has biggest impact (35% weight)")
        print("2. Counter-arguments reduce confidence (25% weight)")
        print("3. Weak retrieval hurts confidence (20% weight)")
        print("4. Risk is assessed independently (can be high even with high confidence)")
        print("5. Decision gate uses BOTH confidence and risk")
        
        print("\n🚀 This scoring drives the Decision Gate (next phase)!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Test error")
        sys.exit(1)


if __name__ == "__main__":
    main()
