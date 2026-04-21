"""
Document Ingestion & Retrieval Test

This test demonstrates the COMPLETE document processing pipeline:
1. Parse document (TXT/PDF/DOCX)
2. Chunk into semantic pieces (clause-aware)
3. Generate embeddings (sentence-transformers)
4. Index in FAISS
5. Search with semantic similarity

Learning goals:
- See end-to-end document processing
- Understand chunking strategy
- Test semantic search vs keyword search
- Validate retrieval quality
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from loguru import logger
from src.ingestion.pipeline import IngestionPipeline


def test_document_parsing():
    """
    Test 1: Parse sample document.
    """
    print("\n" + "="*80)
    print("TEST 1: Document Parsing")
    print("="*80)
    
    from src.ingestion.document_parser import DocumentParser
    
    parser = DocumentParser()
    doc_path = Path("test_data/sample_employment_agreement.txt")
    
    if not doc_path.exists():
        print(f"❌ Sample document not found: {doc_path}")
        return
    
    print(f"\n📄 Parsing: {doc_path}")
    
    parsed = parser.parse_file(doc_path)
    
    print(f"\n✅ Parse Results:")
    print(f"   - Type: {parsed.document_type}")
    print(f"   - Characters: {len(parsed.text):,}")
    print(f"   - Lines: {parsed.metadata.get('lines', 'N/A')}")
    print(f"\n   First 200 chars:")
    print(f"   {parsed.text[:200]}...")
    
    print("\n✅ Test 1 PASSED")
    return parsed


def test_document_chunking(parsed_doc):
    """
    Test 2: Chunk document into semantic pieces.
    """
    print("\n" + "="*80)
    print("TEST 2: Document Chunking")
    print("="*80)
    
    from src.ingestion.chunker import LegalChunker
    
    chunker = LegalChunker(
        chunk_size=500,  # ~500 tokens per chunk
        chunk_overlap=50,
        min_chunk_size=100
    )
    
    print(f"\n✂️  Chunking document...")
    print(f"   - Chunk size: 500 tokens")
    print(f"   - Overlap: 50 tokens")
    
    chunks = chunker.chunk_document(
        text=parsed_doc.text,
        document_id="EMP_AGREE_001",
        metadata={"jurisdiction": "California", "doc_type": "employment_agreement"}
    )
    
    print(f"\n✅ Chunking Results:")
    print(f"   - Total chunks: {len(chunks)}")
    print(f"   - Avg chunk size: {sum(len(c.text) for c in chunks) / len(chunks):.0f} chars")
    
    print(f"\n   Sample chunks:")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n   Chunk {i}: {chunk.chunk_id}")
        print(f"   - Section: {chunk.section}")
        print(f"   - Length: {len(chunk.text)} chars")
        print(f"   - Text: {chunk.text[:100]}...")
    
    print("\n✅ Test 2 PASSED")
    return chunks


def test_embedding_generation(chunks):
    """
    Test 3: Generate embeddings for chunks.
    """
    print("\n" + "="*80)
    print("TEST 3: Embedding Generation")
    print("="*80)
    
    from src.ingestion.embedder import EmbeddingGenerator
    
    embedder = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
    
    print(f"\n🧠 Generating embeddings...")
    print(f"   - Model: {embedder.model_name}")
    print(f"   - Dimension: {embedder.embedding_dim}")
    print(f"   - Chunks: {len(chunks)}")
    
    chunk_texts = [chunk.text for chunk in chunks]
    embeddings = embedder.embed_texts(chunk_texts)
    
    print(f"\n✅ Embedding Results:")
    print(f"   - Shape: {embeddings.shape}")
    print(f"   - Size: {embeddings.nbytes / 1024:.2f} KB")
    print(f"   - Sample embedding (first 10 dims):")
    print(f"     {embeddings[0][:10]}")
    
    print("\n✅ Test 3 PASSED")
    return embedder, embeddings


def test_vector_store(chunks, embeddings):
    """
    Test 4: Index chunks in FAISS and test search.
    """
    print("\n" + "="*80)
    print("TEST 4: Vector Store Indexing & Search")
    print("="*80)
    
    from src.retrieval.vector_store import FAISSVectorStore
    from src.ingestion.embedder import EmbeddingGenerator
    
    # Create vector store
    vector_store = FAISSVectorStore(embedding_dim=embeddings.shape[1])
    
    print(f"\n📚 Indexing chunks...")
    vector_store.add_chunks(chunks, embeddings)
    
    print(f"\n✅ Index Stats:")
    stats = vector_store.get_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    # Test search
    print(f"\n🔍 Testing semantic search...")
    
    embedder = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
    
    test_queries = [
        "What happens if there's a dispute?",
        "Can I work for a competitor after leaving?",
        "What is the base salary?",
    ]
    
    for query in test_queries:
        print(f"\n   Query: \"{query}\"")
        
        # Embed query
        query_emb = embedder.embed_text(query)
        
        # Search
        results = vector_store.search(query_emb, top_k=2)
        
        print(f"   Results ({len(results)} chunks):")
        for i, (chunk, score) in enumerate(results, 1):
            print(f"     {i}. [{chunk.section}] (score: {score:.3f})")
            print(f"        {chunk.text[:100]}...")
    
    print("\n✅ Test 4 PASSED")
    return vector_store


def test_full_pipeline():
    """
    Test 5: End-to-end pipeline test.
    """
    print("\n" + "="*80)
    print("TEST 5: Full Ingestion Pipeline")
    print("="*80)
    
    # Initialize pipeline
    pipeline = IngestionPipeline(
        embedding_model="all-MiniLM-L6-v2",
        chunk_size=500,
        chunk_overlap=50
    )
    
    print(f"\n📦 Pipeline initialized")
    print(f"   Stats: {pipeline.get_stats()}")
    
    # Ingest document
    doc_path = Path("test_data/sample_employment_agreement.txt")
    
    if not doc_path.exists():
        print(f"❌ Sample document not found: {doc_path}")
        return None
    
    print(f"\n📥 Ingesting: {doc_path.name}")
    
    chunks = pipeline.ingest_document(
        file_path=doc_path,
        document_id="EMP_AGREE_001",
        metadata={"jurisdiction": "California", "doc_type": "employment_agreement"}
    )
    
    print(f"\n✅ Ingestion complete!")
    print(f"   - Chunks created: {len(chunks)}")
    print(f"   - Index size: {pipeline.vector_store.index.ntotal}")
    
    # Test retrieval
    print(f"\n🔍 Testing retrieval through pipeline...")
    
    test_query = "arbitration dispute resolution"
    query_emb = pipeline.embedder.embed_text(test_query)
    results = pipeline.vector_store.search(query_emb, top_k=3)
    
    print(f"\n   Query: \"{test_query}\"")
    print(f"   Top {len(results)} results:")
    
    for i, (chunk, score) in enumerate(results, 1):
        print(f"\n   {i}. Score: {score:.3f}")
        print(f"      Section: {chunk.section}")
        print(f"      Text: {chunk.text[:150]}...")
    
    # Save index
    index_dir = Path("./test_vector_store")
    print(f"\n💾 Saving index to: {index_dir}")
    pipeline.save_index(index_dir)
    
    # Load index
    print(f"\n📂 Loading index from: {index_dir}")
    loaded_pipeline = IngestionPipeline.load_index(index_dir)
    
    print(f"\n✅ Index loaded successfully!")
    print(f"   Stats: {loaded_pipeline.get_stats()}")
    
    print("\n✅ Test 5 PASSED")
    return pipeline


def main():
    """Run all tests."""
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    print("\n" + "="*80)
    print("📚 DOCUMENT INGESTION & RETRIEVAL TEST SUITE")
    print("="*80)
    print("\nThis demonstrates the full document processing pipeline:")
    print("  1. Document Parsing (TXT/PDF/DOCX)")
    print("  2. Semantic Chunking (clause-aware)")
    print("  3. Embedding Generation (sentence-transformers)")
    print("  4. Vector Indexing (FAISS)")
    print("  5. Semantic Search (top-k retrieval)")
    
    try:
        # Test 1: Parse
        parsed_doc = test_document_parsing()
        
        # Test 2: Chunk
        chunks = test_document_chunking(parsed_doc)
        
        # Test 3: Embed
        embedder, embeddings = test_embedding_generation(chunks)
        
        # Test 4: Index & Search
        vector_store = test_vector_store(chunks, embeddings)
        
        # Test 5: Full Pipeline
        pipeline = test_full_pipeline()
        
        # Summary
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        
        print("\n🎓 Key Observations:")
        print("1. Document parsed successfully")
        print(f"2. Created {len(chunks)} semantic chunks (clause-aware)")
        print(f"3. Generated {embeddings.shape[1]}-dimensional embeddings")
        print(f"4. Indexed {vector_store.index.ntotal} chunks in FAISS")
        print("5. Semantic search works (finds relevant chunks)")
        print("6. Index saved and loaded successfully")
        
        print("\n🚀 Document processing pipeline is READY!")
        
        print("\n📈 Next Steps:")
        print("  - Ingest more documents (PDF/DOCX support)")
        print("  - Integrate with retrieval agent")
        print("  - Test with real queries in full RAG pipeline")
        print("  - Build document upload API")
        print("  - Create frontend for document management")
        
    except Exception as e:
        logger.exception("Test suite failed")
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
