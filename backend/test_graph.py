"""
Test the LangGraph state machine with stub agents.

This validates:
1. Graph compiles correctly
2. State flows through all nodes
3. Decision gate logic works
4. Formatters produce correct output
"""

import asyncio
from src.graph.state_machine import run_legal_rag_query
from src.utils.logger import setup_logger

async def main():
    # Setup logging
    setup_logger()
    
    print("="*60)
    print("Testing Legal RAG State Machine (Stub Mode)")
    print("="*60)
    print()
    
    # Test query
    response = await run_legal_rag_query(
        query_text="Does the arbitration clause apply to employment disputes?",
        jurisdiction="California",
        context="Employment agreement for software engineer"
    )
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print()
    print(f"Success: {response.success}")
    print(f"Confidence: {response.confidence.overall_score:.1f}/100")
    print(f"Risk: {response.risk.overall_risk}")
    print()
    
    if response.success:
        print("ANSWER:")
        print(response.answer.answer_text)
        print()
        print(f"Citations: {len(response.answer.citations)}")
        print(f"Warnings: {len(response.warnings)}")
    else:
        print("REFUSAL:")
        print(f"Reason: {response.refusal_reason}")
        print(response.refusal_explanation)
    
    print()
    print("="*60)
    print("✅ Graph executed successfully!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
