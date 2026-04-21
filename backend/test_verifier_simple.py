"""
Simplified Citation Verifier Test - No Heavy Dependencies

This is a lightweight test that directly tests the core verification logic
without loading the full application context.
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent / "src"
sys.path.insert(0, str(backend_src))

print("Testing imports...")

# Test basic imports
try:
    from schemas.answer import Answer, Citation
    print("✅ Imported Answer and Citation schemas")
except Exception as e:
    print(f"❌ Failed to import Answer/Citation: {e}")
    sys.exit(1)

try:
    from schemas.retrieval import RetrievedClause
    print("✅ Imported RetrievedClause schema")
except Exception as e:
    print(f"❌ Failed to import RetrievedClause: {e}")
    sys.exit(1)

try:
    from agents.verifier import CitationVerifier
    print("✅ Imported CitationVerifier")
except Exception as e:
    print(f"❌ Failed to import CitationVerifier: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("TEST: Valid Citation Verification")
print("="*80)

# Create mock data
retrieved_clauses = [
    RetrievedClause(
        clause_id="DOC1_SEC5.2",
        text="The Employee agrees not to disclose any Confidential Information to third parties without prior written consent from the Employer.",
        document_id="DOC1",
        section="Section 5.2 - Confidentiality",
        similarity_score=0.92,
        metadata={"jurisdiction": "California"}
    ),
]

answer = Answer(
    answer_text="Employees cannot share confidential information.",
    citations=[
        Citation(
            clause_id="DOC1_SEC5.2",
            quoted_text="The Employee agrees not to disclose any Confidential Information to third parties",
            reasoning="This clause prohibits disclosure"
        ),
    ],
    reasoning="Based on confidentiality clause",
    assumptions=[],
    caveats=[]
)

# Test verification
print("\nRunning verification...")
verifier = CitationVerifier(use_llm_reasoning_check=False)
result = verifier.verify_answer(answer, retrieved_clauses)

print(f"\n✅ Verification complete!")
print(f"Total citations: {result.total_citations}")
print(f"Valid citations: {result.valid_citations}")
print(f"Invalid citations: {result.invalid_citations}")
print(f"All valid: {result.all_citations_valid}")

if result.all_citations_valid:
    print("\n🎉 SUCCESS: Citation verification working correctly!")
else:
    print("\n❌ FAILED: Citation marked as invalid")
    for issue in result.verification_issues:
        print(f"  - {issue}")
