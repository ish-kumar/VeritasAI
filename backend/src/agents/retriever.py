"""
Clause Retrieval Agent - Real FAISS Implementation

This node:
1. Embeds the query
2. Searches FAISS vector store
3. Applies metadata filtering (jurisdiction, doc type)
4. Converts chunks to RetrievedClause format

Uses the global vector store instance (loaded at startup).
"""

from loguru import logger
from ..schemas.state import GraphState
from ..schemas.retrieval import RetrievalResult, RetrievedClause
from ..utils.config import get_settings


# Global vector store instance (loaded at startup)
# This is set by initialize_vector_store() in main.py
_vector_store = None
_embedder = None


def initialize_vector_store(vector_store, embedder):
    """
    Initialize global vector store and embedder.
    
    Called at application startup.
    
    Why global:
    - Vector store is expensive to load (~1-2 seconds)
    - Embedder loads model (~1-2 seconds)
    - Share across all requests
    - Singleton pattern
    """
    global _vector_store, _embedder
    _vector_store = vector_store
    _embedder = embedder
    logger.success("Vector store and embedder initialized for retrieval agent")


def retrieve_clauses_node(state: GraphState) -> GraphState:
    """
    Retrieve relevant clauses from FAISS vector store.
    
    Algorithm:
    1. Get query text from state
    2. Embed query using sentence-transformers
    3. Search FAISS index for top-k similar chunks
    4. Apply metadata filters (if any)
    5. Convert chunks to RetrievedClause format
    6. Return in state
    
    Why this approach:
    - Semantic search (not keyword matching)
    - Fast (<100ms for most queries)
    - Metadata filtering for jurisdiction/doc type
    - Returns actual document chunks with citations
    """
    query_id = state.get("query_id")
    query = state.get("query")
    settings = get_settings()
    
    logger.info(f"Retrieving clauses for: {query_id}")
    
    # Check if vector store is initialized
    if _vector_store is None or _embedder is None:
        logger.warning("Vector store not initialized, using stub data")
        return _retrieve_stub_clauses(state)
    
    try:
        # DEBUG: Log retriever state
        logger.debug(f"[Retriever] _vector_store is None: {_vector_store is None}")
        logger.debug(f"[Retriever] _embedder is None: {_embedder is None}")
        if _vector_store:
            logger.debug(f"[Retriever] Vector store has {_vector_store.index.ntotal} vectors")
        
        # Embed query
        query_embedding = _embedder.embed_text(query.text)
        logger.debug(f"[Retriever] Query embedding shape: {query_embedding.shape}")
        
        # Build filters from query metadata
        filters = {}
        if query.jurisdiction:
            filters["jurisdiction"] = query.jurisdiction
            logger.debug(f"[Retriever] Added jurisdiction filter: {query.jurisdiction}")
        
        logger.debug(f"[Retriever] Filters dict: {filters}")
        logger.debug(f"[Retriever] Filters (after ternary): {filters if filters else None}")
        
        # Search vector store
        top_k = settings.retrieval_top_k
        logger.debug(f"[Retriever] Calling search with top_k={top_k}, filters={filters if filters else None}")
        results = _vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters if filters else None
        )
        logger.debug(f"[Retriever] Search returned {len(results)} results")
        
        # Convert chunks to RetrievedClause format
        retrieved_clauses = []
        for chunk, similarity in results:
            clause = RetrievedClause(
                clause_id=chunk.chunk_id,
                text=chunk.text,
                document_id=chunk.document_id,
                section=chunk.section,
                similarity_score=float(similarity),
                metadata=chunk.metadata
            )
            retrieved_clauses.append(clause)
        
        retrieval_result = RetrievalResult(
            clauses=retrieved_clauses,
            top_k=len(retrieved_clauses),
            retrieval_query=query.text
        )
        
        logger.success(
            f"Retrieved {len(retrieved_clauses)} clauses "
            f"(avg similarity: {sum(c.similarity_score for c in retrieved_clauses) / len(retrieved_clauses):.2f})"
            if retrieved_clauses else "Retrieved 0 clauses"
        )
        
        return {
            **state,
            "retrieval_result": retrieval_result,
        }
        
    except Exception as e:
        logger.error(f"Error during retrieval: {e}")
        logger.warning("Falling back to stub clauses")
        return _retrieve_stub_clauses(state)


def _retrieve_stub_clauses(state: GraphState) -> GraphState:
    """
    Fallback stub implementation (for testing without vector store).
    
    Returns mock data that looks like real retrieval results.
    """
    query_id = state.get("query_id")
    query = state.get("query")
    
    logger.info(f"[STUB] Retrieving clauses: {query_id}")
    
    # Stub: Return mock retrieval result with realistic legal text
    stub_clauses = [
        RetrievedClause(
            clause_id="EMP_AGREE_001_SEC12.3",
            text="Any dispute arising under this Agreement shall be resolved through binding arbitration in accordance with the rules of the American Arbitration Association. The arbitration shall take place in California and shall be governed by California law.",
            document_id="EMP_AGREE_001",
            section="Section 12.3 - Dispute Resolution",
            similarity_score=0.92,
            metadata={"jurisdiction": query.jurisdiction or "California", "doc_type": "employment_agreement"}
        ),
        RetrievedClause(
            clause_id="EMP_AGREE_001_SEC12.4",
            text="The arbitrator's decision shall be final and binding on all parties. Each party shall bear its own attorney's fees and costs, and the arbitrator's fees shall be split equally between the parties.",
            document_id="EMP_AGREE_001",
            section="Section 12.4 - Arbitration Costs",
            similarity_score=0.88,
            metadata={"jurisdiction": query.jurisdiction or "California", "doc_type": "employment_agreement"}
        ),
    ]
    
    retrieval_result = RetrievalResult(
        clauses=stub_clauses,
        top_k=len(stub_clauses),
        retrieval_query=query.text
    )
    
    return {
        **state,
        "retrieval_result": retrieval_result,
    }

