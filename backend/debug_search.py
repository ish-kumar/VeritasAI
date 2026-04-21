"""
Debug script to test FAISS search.
"""

import sys
from pathlib import Path

# Add src to path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(src_dir))

from src.ingestion.pipeline import IngestionPipeline

# Load the pipeline
pipeline = IngestionPipeline.load_index(Path("./vector_store"))

print(f"Loaded pipeline with {pipeline.vector_store.index.ntotal} chunks")
print(f"Chunks in metadata: {len(pipeline.vector_store.chunks)}")
print(f"Embedding dimension: {pipeline.embedder.embedding_dim}")
print(f"FAISS index dimension: {pipeline.vector_store.index.d}")

# Test query
query = "What is the base salary?"
print(f"\nQuerying: '{query}'")

# Embed query
query_embedding = pipeline.embedder.embed_text(query)
print(f"Query embedding shape: {query_embedding.shape}")
print(f"Query embedding sample: {query_embedding[:5]}")

# Raw FAISS search
similarities, indices = pipeline.vector_store.index.search(query_embedding.reshape(1, -1), 5)
print(f"\nRaw FAISS search results:")
print(f"Indices: {indices}")
print(f"Similarities: {similarities}")

# Check chunk at index 0
if len(pipeline.vector_store.chunks) > 0:
    chunk = pipeline.vector_store.chunks[0]
    print(f"\nFirst chunk:")
    print(f"  ID: {chunk.chunk_id}")
    print(f"  Text: {chunk.text[:100]}...")
    print(f"  Section: {chunk.section}")

# Try the high-level search
results = pipeline.vector_store.search(query_embedding, top_k=5)
print(f"\nHigh-level search returned {len(results)} results")
for i, (chunk, sim) in enumerate(results[:3]):
    print(f"{i+1}. {chunk.section}: {chunk.text[:50]}... (sim: {sim:.3f})")
