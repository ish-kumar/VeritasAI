#!/usr/bin/env python3
"""
Quick script to ingest all test documents into the vector store.
Run this to populate your system with sample legal documents for testing.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion.pipeline import DocumentIngestionPipeline
from src.retrieval.vector_store import VectorStore
from src.utils.logger import logger


async def ingest_all_test_documents():
    """Ingest all documents from test_data directory."""
    
    # Initialize components
    vector_store = VectorStore()
    pipeline = DocumentIngestionPipeline(vector_store=vector_store)
    
    # Get all test documents
    test_data_dir = Path(__file__).parent / "test_data"
    document_files = [
        test_data_dir / "sample_employment_agreement.txt",
        test_data_dir / "sample_nda.txt",
        test_data_dir / "sample_lease.txt",
    ]
    
    print("=" * 70)
    print("📚 INGESTING TEST DOCUMENTS")
    print("=" * 70)
    print()
    
    total_chunks = 0
    
    for doc_path in document_files:
        if not doc_path.exists():
            print(f"⚠️  Skipping {doc_path.name} (not found)")
            continue
            
        print(f"📄 Processing: {doc_path.name}")
        print(f"   Size: {doc_path.stat().st_size:,} bytes")
        
        try:
            # Read file content
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ingest document
            result = await pipeline.ingest_document(
                content=content,
                filename=doc_path.name,
                metadata={
                    "source": "test_data",
                    "doc_type": _get_doc_type(doc_path.name),
                }
            )
            
            if result['success']:
                chunks_added = result['chunks_added']
                total_chunks += chunks_added
                print(f"   ✅ Success! Added {chunks_added} chunks")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            logger.exception(f"Failed to ingest {doc_path.name}")
        
        print()
    
    # Save vector store
    print("💾 Saving vector store...")
    vector_store.save()
    
    print("=" * 70)
    print(f"✅ INGESTION COMPLETE")
    print(f"   Total documents: {len(document_files)}")
    print(f"   Total chunks: {total_chunks}")
    print(f"   Vector store: {vector_store._store_path}")
    print("=" * 70)
    print()
    print("🚀 Ready to test! Start the backend and try queries from TEST_QUERIES.md")
    print()


def _get_doc_type(filename: str) -> str:
    """Determine document type from filename."""
    if "employment" in filename.lower():
        return "employment_agreement"
    elif "nda" in filename.lower():
        return "non_disclosure_agreement"
    elif "lease" in filename.lower():
        return "commercial_lease"
    else:
        return "unknown"


if __name__ == "__main__":
    asyncio.run(ingest_all_test_documents())
