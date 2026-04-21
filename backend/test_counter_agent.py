"""
Test Answer Agent + Counter-Agent together.
Shows the adversarial interaction.
"""

import asyncio
from src.schemas.query import Query, QueryType
from src.schemas.retrieval import RetrievalResult, RetrievedClause
from src.schemas.state import GraphState
from src.agents.answer import generate_answer_node
from src.agents.counter import generate_counter_node
from src.utils.logger import setup_logger


async def main():
    setup_logger()
    
    print("=" * 70)
    print("Testing Answer Agent + Counter-Agent (Adversarial)")
    print("=" * 70)
    print()
    
    # Create query
    query = Query(
        text="Does the arbitration clause in Section 12.3 apply to employment disputes?",
        query_type=QueryType.INTERPRETIVE,
        jurisdiction="California"
    )
    
    # Sample clauses (same as before)
    sample_clauses = [
        RetrievedClause(
            clause_id="SEC_12.3",
            text=(
                "Any dispute, controversy, or claim arising out of or relating to this Agreement, "
                "including but not limited to employment-related claims, shall be resolved through "
                "binding arbitration in accordance with the rules of the American Arbitration Association."
            ),
            document_id="EMP_AGREEMENT_2023",
            section="Section 12.3 - Dispute Resolution",
            similarity_score=0.92,
            metadata={"jurisdiction": "California", "document_type": "employment_agreement"}
        ),
        RetrievedClause(
            clause_id="SEC_12.4",
            text=(
                "Notwithstanding Section 12.3, the following claims are excluded from arbitration: "
                "(a) claims brought under the California Private Attorneys General Act (PAGA), "
                "(b) claims for workers' compensation benefits."
            ),
            document_id="EMP_AGREEMENT_2023",
            section="Section 12.4 - Exceptions to Arbitration",
            similarity_score=0.85,
            metadata={"jurisdiction": "California", "document_type": "employment_agreement"}
        ),
    ]
    
    retrieval_result = RetrievalResult(
        clauses=sample_clauses,
        top_k=2,
        retrieval_query="arbitration employment disputes"
    )
    
    # Initial state
    state: GraphState = {
        "query": query,
        "query_id": "test_adversarial_001",
        "retrieval_result": retrieval_result,
    }
    
    print("📝 Query:", query.text)
    print()
    
    # Step 1: Generate Answer
    print("🔵 STEP 1: Answer Agent (Blue Team)")
    print("-" * 70)
    state = await generate_answer_node(state)
    answer = state["answer"]
    
    print(f"Answer: {answer.answer_text}")
    print(f"Citations: {len(answer.citations)}")
    print()
    
    # Step 2: Generate Counter-Arguments
    print("🔴 STEP 2: Counter-Agent (Red Team)")
    print("-" * 70)
    state = await generate_counter_node(state)
    counter = state["counter_arguments"]
    
    print(f"Severity: {counter.severity}")
    print()
    
    if counter.contradictions:
        print(f"⚠️  CONTRADICTIONS ({len(counter.contradictions)}):")
        for c in counter.contradictions:
            print(f"   - {c}")
        print()
    
    if counter.exceptions:
        print(f"📋 EXCEPTIONS ({len(counter.exceptions)}):")
        for e in counter.exceptions:
            print(f"   - {e}")
        print()
    
    if counter.jurisdictional_issues:
        print(f"🏛️  JURISDICTIONAL ISSUES ({len(counter.jurisdictional_issues)}):")
        for j in counter.jurisdictional_issues:
            print(f"   - {j}")
        print()
    
    if counter.ambiguities:
        print(f"❓ AMBIGUITIES ({len(counter.ambiguities)}):")
        for a in counter.ambiguities:
            print(f"   - {a}")
        print()
    
    if counter.missing_context:
        print(f"🔍 MISSING CONTEXT ({len(counter.missing_context)}):")
        for m in counter.missing_context:
            print(f"   - {m}")
        print()
    
    if counter.alternative_interpretation:
        print("💭 ALTERNATIVE INTERPRETATION:")
        print(f"   {counter.alternative_interpretation}")
        print()
    
    print("=" * 70)
    print("✅ Adversarial validation complete!")
    print("=" * 70)
    print()
    print(f"Summary: Answer generated, challenged with {counter.severity} severity")


if __name__ == "__main__":
    asyncio.run(main())
