"""
Check chunk metadata to debug filtering issue.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ingestion.pipeline import IngestionPipeline

# Load pipeline
pipeline = IngestionPipeline.load_index(Path("./vector_store"))

print(f"Total chunks: {len(pipeline.vector_store.chunks)}")
print(f"FAISS index total: {pipeline.vector_store.index.ntotal}")

# Check first few chunks
for i, chunk in enumerate(pipeline.vector_store.chunks[:5]):
    print(f"\n--- Chunk {i} ---")
    print(f"ID: {chunk.chunk_id}")
    print(f"Document ID: {chunk.document_id}")
    print(f"Section: {chunk.section}")
    print(f"Text: {chunk.text[:80]}...")
    print(f"Metadata: {chunk.metadata}")

# Try a search with no filters
print("\n\n=== Testing search with no filters ===")
query = "base salary"
query_emb = pipeline.embedder.embed_text(query)
results = pipeline.vector_store.search(query_emb, top_k=5, filters=None)
print(f"Results with filters=None: {len(results)}")
for i, (chunk, sim) in enumerate(results[:3]):
    print(f"{i+1}. [{chunk.section}] {chunk.text[:50]}... (sim: {sim:.3f})")

# Try with empty dict
results2 = pipeline.vector_store.search(query_emb, top_k=5, filters={})
print(f"\nResults with filters={{}}: {len(results2)}")

# Try without filters parameter at all
import numpy as np
print(f"\n=== Raw FAISS search ===")
q = query_emb.reshape(1, -1).astype(np.float32)
import faiss
faiss.normalize_L2(q)
similarities, indices = pipeline.vector_store.index.search(q, 5)
print(f"Indices: {indices}")
print(f"Similarities: {similarities}")
print(f"Are any indices < 0? {any(idx < 0 for idx in indices[0])}")
print(f"Are any indices >= len(chunks)? {any(idx >= len(pipeline.vector_store.chunks) for idx in indices[0] if idx >= 0)}")
