"""
Test the Answer Agent with real LLM integration.

This script:
1. Creates a mock retrieval result with sample legal clauses
2. Runs the Answer Agent
3. Displays the generated answer with citations

Prerequisites:
- GROQ_API_KEY in .env file
- All packages installed
"""

import asyncio
from src.schemas.query import Query, QueryType
from src.schemas.retrieval import RetrievalResult, RetrievedClause
from src.schemas.state import GraphState
from src.agents.answer import generate_answer_node
from src.utils.logger import setup_logger


async def main():
    # Setup logging
    setup_logger()
    
    print("=" * 70)
    print("Testing Answer Agent with Real LLM (Groq)")
    print("=" * 70)
    print()
    
    # Create sample query
    query = Query(
        text="Does the arbitration clause in Section 12.3 apply to employment disputes?",
        query_type=QueryType.INTERPRETIVE,
        jurisdiction="California",
        context="This is regarding a software engineer's employment agreement"
    )
    
    # Create mock retrieval result with sample legal clauses
    # (In production, these would come from the retriever)
    sample_clauses = [
        RetrievedClause(
            clause_id="SEC_12.3",
            text=(
                "Any dispute, controversy, or claim arising out of or relating to this Agreement, "
                "including but not limited to employment-related claims, shall be resolved through "
                "binding arbitration in accordance with the rules of the American Arbitration Association. "
                "The arbitration shall take place in San Francisco, California."
            ),
            document_id="EMP_AGREEMENT_2023",
            section="Section 12.3 - Dispute Resolution",
            similarity_score=0.92,
            metadata={
                "jurisdiction": "California",
                "document_type": "employment_agreement",
                "effective_date": "2023-01-15"
            }
        ),
        RetrievedClause(
            clause_id="SEC_12.4",
            text=(
                "Notwithstanding Section 12.3, the following claims are excluded from arbitration: "
                "(a) claims brought under the California Private Attorneys General Act (PAGA), "
                "(b) claims for workers' compensation benefits, and "
                "(c) claims for unemployment insurance benefits."
            ),
            document_id="EMP_AGREEMENT_2023",
            section="Section 12.4 - Exceptions to Arbitration",
            similarity_score=0.85,
            metadata={
                "jurisdiction": "California",
                "document_type": "employment_agreement",
                "effective_date": "2023-01-15"
            }
        ),
        RetrievedClause(
            clause_id="SEC_1.2",
            text=(
                "This Agreement shall be governed by and construed in accordance with the laws "
                "of the State of California, without regard to its conflict of law principles."
            ),
            document_id="EMP_AGREEMENT_2023",
            section="Section 1.2 - Governing Law",
            similarity_score=0.78,
            metadata={
                "jurisdiction": "California",
                "document_type": "employment_agreement",
                "effective_date": "2023-01-15"
            }
        ),
    ]
    
    retrieval_result = RetrievalResult(
        clauses=sample_clauses,
        top_k=3,
        retrieval_query="arbitration clause employment disputes California"
    )
    
    # Create initial state
    state: GraphState = {
        "query": query,
        "query_id": "test_001",
        "retrieval_result": retrieval_result,
    }
    
    print("📝 Query:")
    print(f"   {query.text}")
    print()
    print(f"📚 Retrieved {len(sample_clauses)} clauses")
    print()
    print("⏳ Calling Groq LLM (Llama 3.1 70B)...")
    print("   This may take 2-5 seconds...")
    print()
    
    try:
        # Run Answer Agent
        result_state = await generate_answer_node(state)
        
        # Extract answer
        answer = result_state.get("answer")
        
        if not answer:
            print("❌ Error: No answer generated")
            if result_state.get("error"):
                print(f"   Error: {result_state['error']}")
            return
        
        print("=" * 70)
        print("✅ ANSWER GENERATED")
        print("=" * 70)
        print()
        
        print("📄 ANSWER:")
        print(f"   {answer.answer_text}")
        print()
        
        print(f"📎 CITATIONS ({len(answer.citations)}):")
        for i, cite in enumerate(answer.citations, 1):
            print(f"\n   [{i}] Clause: {cite.clause_id}")
            print(f"       Quote: \"{cite.quoted_text[:100]}...\"" if len(cite.quoted_text) > 100 else f"       Quote: \"{cite.quoted_text}\"")
            print(f"       Reasoning: {cite.reasoning}")
        print()
        
        print("💭 REASONING:")
        print(f"   {answer.reasoning}")
        print()
        
        if answer.assumptions:
            print(f"🤔 ASSUMPTIONS ({len(answer.assumptions)}):")
            for assumption in answer.assumptions:
                print(f"   - {assumption}")
            print()
        
        if answer.caveats:
            print(f"⚠️  CAVEATS ({len(answer.caveats)}):")
            for caveat in answer.caveats:
                print(f"   - {caveat}")
            print()
        
        print("=" * 70)
        print("🎉 Success! Answer Agent is working with real LLM!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. ✅ Answer Agent working")
        print("2. 🔜 Implement Counter-Argument Agent (Phase 2B)")
        print("3. 🔜 Implement Citation Verifier (Phase 2C)")
        print("4. 🔜 Implement Confidence Scorer (Phase 2D)")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        print()
        print("Common issues:")
        print("- Missing GROQ_API_KEY in .env file")
        print("- Network connectivity")
        print("- Invalid .env configuration")
        print()
        print("Check logs/app.log for details")
        raise


if __name__ == "__main__":
    asyncio.run(main())
