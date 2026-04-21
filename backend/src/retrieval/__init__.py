"""
Retrieval system - Vector search and document retrieval.

Components:
- FAISS vector store (fast similarity search)
- Metadata filtering
- Re-ranking (optional)
"""

from .vector_store import FAISSVectorStore

__all__ = ["FAISSVectorStore"]
