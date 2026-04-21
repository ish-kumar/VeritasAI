"""
FAISS Vector Store - Fast similarity search for document chunks.

Why FAISS:
✅ Blazing fast (Facebook's production-grade library)
✅ Scales to millions of vectors
✅ Multiple index types (flat, IVF, HNSW)
✅ In-memory or disk-based
✅ No external database needed

Architecture:
- Index: Stores vector embeddings
- Metadata: Stores chunk info (text, doc_id, section, etc.)
- Search: K-nearest neighbors by cosine similarity
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import pickle
import numpy as np

from loguru import logger

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("faiss-cpu not installed")

from ..ingestion.chunker import DocumentChunk


class FAISSVectorStore:
    """
    FAISS-based vector store for semantic search.
    
    Design:
    - index: FAISS index (stores vectors)
    - chunks: List of DocumentChunk objects (stores metadata)
    - Index position i corresponds to chunks[i]
    
    Why store chunks separately:
    - FAISS only stores vectors (no metadata)
    - We need chunk text, IDs, metadata for retrieval
    - Simple list keeps everything aligned
    
    Index types:
    - IndexFlatL2: Exact search, slow for large datasets
    - IndexFlatIP: Exact inner product search (for cosine)
    - IndexIVFFlat: Approximate search, faster for large datasets
    - IndexHNSW: Graph-based, very fast
    
    For our use case:
    - Start with IndexFlatIP (exact, simple)
    - Upgrade to IndexIVFFlat if >10K chunks
    - Use IndexHNSW for >100K chunks
    """
    
    def __init__(self, embedding_dim: int, index_type: str = "flat"):
        """
        Initialize FAISS vector store.
        
        Args:
            embedding_dim: Dimension of embedding vectors
            index_type: Type of FAISS index ("flat", "ivf", "hnsw")
            
        Why IndexFlatIP:
        - IP = Inner Product
        - For normalized vectors, IP = cosine similarity
        - Exact search (no approximation)
        - Simple and reliable
        """
        if not FAISS_AVAILABLE:
            raise ImportError(
                "faiss-cpu not installed. "
                "Install with: pip install faiss-cpu"
            )
        
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        
        # Create FAISS index
        if index_type == "flat":
            # Flat index: Exact search using inner product (cosine for normalized vectors)
            self.index = faiss.IndexFlatIP(embedding_dim)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
        
        # Store chunks (metadata)
        self.chunks: List[DocumentChunk] = []
        
        logger.info(
            f"Initialized FAISS index: {index_type}, dim={embedding_dim}"
        )
    
    def add_chunks(
        self,
        chunks: List[DocumentChunk],
        embeddings: np.ndarray
    ):
        """
        Add chunks and their embeddings to the index.
        
        Args:
            chunks: List of DocumentChunk objects
            embeddings: Numpy array of shape (len(chunks), embedding_dim)
            
        Why separate chunks and embeddings:
        - Embedding generation is separate step
        - Can batch embed efficiently
        - Can swap embedding models
        
        Learning insight:
        - FAISS index and chunks list must stay aligned
        - Index position i → chunks[i]
        - Never modify chunks list directly after adding to index
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) "
                "must have same length"
            )
        
        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(
                f"Embedding dim ({embeddings.shape[1]}) doesn't match "
                f"index dim ({self.embedding_dim})"
            )
        
        # Ensure embeddings are float32 (FAISS requirement)
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32)
        
        # Ensure normalized for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        # Add to chunks list
        self.chunks.extend(chunks)
        
        logger.info(
            f"Added {len(chunks)} chunks to index. "
            f"Total: {self.index.ntotal} chunks"
        )
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[tuple[DocumentChunk, float]]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query vector of shape (embedding_dim,)
            top_k: Number of results to return
            filters: Optional metadata filters (e.g., {"jurisdiction": "California"})
            
        Returns:
            List of (chunk, similarity_score) tuples, sorted by similarity
            
        Similarity score:
        - Range: [-1, 1] for inner product
        - For normalized vectors: cosine similarity
        - Higher = more similar
        
        Filtering:
        - FAISS doesn't support metadata filtering natively
        - We post-filter results after search
        - For production: Use pgvector or Pinecone for native filtering
        """
        if self.index.ntotal == 0:
            logger.warning("Index is empty, no results")
            return []
        
        # Ensure query is correct shape and type
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        if query_embedding.dtype != np.float32:
            query_embedding = query_embedding.astype(np.float32)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        # We fetch more than top_k to account for filtering
        fetch_k = top_k * 3 if filters else top_k
        fetch_k = min(fetch_k, self.index.ntotal)  # Don't fetch more than we have
        
        similarities, indices = self.index.search(query_embedding, fetch_k)
        
        # Convert to list of (chunk, score) tuples
        results = []
        for idx, similarity in zip(indices[0], similarities[0]):
            if idx < 0 or idx >= len(self.chunks):
                # FAISS returns -1 for empty slots
                continue
            
            chunk = self.chunks[idx]
            
            # Apply filters if provided
            if filters and not self._matches_filters(chunk, filters):
                continue
            
            results.append((chunk, float(similarity)))
            
            # Stop once we have enough results
            if len(results) >= top_k:
                break
        
        logger.info(
            f"Found {len(results)} results "
            f"(searched {fetch_k} candidates)"
        )
        
        return results
    
    @staticmethod
    def _matches_filters(chunk: DocumentChunk, filters: Dict[str, Any]) -> bool:
        """
        Check if chunk matches metadata filters.
        
        Args:
            chunk: DocumentChunk to check
            filters: Dict of metadata filters
            
        Returns:
            True if chunk matches all filters
            
        Filter examples:
        - {"jurisdiction": "California"}
        - {"doc_type": "employment_agreement"}
        - {"jurisdiction": "California", "year": 2024}
        
        Why post-filtering:
        - FAISS doesn't support metadata filtering
        - Simple dict matching works for small datasets
        - For production: Use pgvector or Pinecone
        """
        for key, value in filters.items():
            if key not in chunk.metadata:
                return False
            if chunk.metadata[key] != value:
                return False
        return True
    
    def save(self, directory: str | Path):
        """
        Save index and chunks to disk.
        
        Args:
            directory: Directory to save to
            
        Saves:
        - index.faiss: FAISS index
        - chunks.pkl: Pickled list of chunks
        
        Why save:
        - Don't re-index on every startup
        - Faster loading than re-embedding
        - Persist across restarts
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = directory / "index.faiss"
        faiss.write_index(self.index, str(index_path))
        
        # Save chunks
        chunks_path = directory / "chunks.pkl"
        with open(chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
        
        logger.success(
            f"Saved index ({self.index.ntotal} vectors) to {directory}"
        )
    
    @classmethod
    def load(cls, directory: str | Path) -> "FAISSVectorStore":
        """
        Load index and chunks from disk.
        
        Args:
            directory: Directory to load from
            
        Returns:
            Loaded FAISSVectorStore instance
            
        Why classmethod:
        - Alternative constructor
        - Don't need to call __init__ first
        - Clean API: vector_store = FAISSVectorStore.load("path")
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        index_path = directory / "index.faiss"
        chunks_path = directory / "chunks.pkl"
        
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        if not chunks_path.exists():
            raise FileNotFoundError(f"Chunks file not found: {chunks_path}")
        
        # Load FAISS index
        index = faiss.read_index(str(index_path))
        
        # Load chunks
        with open(chunks_path, 'rb') as f:
            chunks = pickle.load(f)
        
        # Create instance
        instance = cls(
            embedding_dim=index.d,  # Get dimension from loaded index
            index_type="flat"
        )
        instance.index = index
        instance.chunks = chunks
        
        logger.success(
            f"Loaded index ({index.ntotal} vectors) from {directory}"
        )
        
        return instance
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the index.
        
        Returns:
            Dict with index stats
            
        Useful for:
        - Monitoring
        - Debugging
        - Displaying to users
        """
        return {
            "total_chunks": self.index.ntotal,
            "embedding_dim": self.embedding_dim,
            "index_type": self.index_type,
            "memory_bytes": self.index.ntotal * self.embedding_dim * 4,  # float32
        }
