"""
pgvector retrieval backend for Supabase Postgres.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor
from loguru import logger

from ..utils.config import get_settings


@dataclass
class PGChunk:
    """
    Shape-compatible chunk object for retrieval agent conversion.
    """
    chunk_id: str
    text: str
    document_id: str
    section: str
    metadata: Dict[str, Any]


class PGVectorStore:
    """
    Minimal pgvector search wrapper.
    """

    def __init__(self, db_url: str):
        self.db_url = db_url

    @classmethod
    def from_settings(cls) -> "PGVectorStore":
        settings = get_settings()
        if not settings.supabase_db_url:
            raise ValueError("SUPABASE_DB_URL is required for pgvector retrieval mode.")
        return cls(settings.supabase_db_url)

    @staticmethod
    def _vector_literal(query_embedding) -> str:
        # pgvector input format: [0.1,0.2,...]
        return "[" + ",".join(str(float(x)) for x in query_embedding.tolist()) + "]"

    def search(
        self,
        query_embedding,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[PGChunk, float]]:
        """
        Query top-k chunks by cosine distance in pgvector.
        """
        filters = filters or {}
        jurisdiction = filters.get("jurisdiction")
        vector_param = self._vector_literal(query_embedding)

        sql = """
            select
                clause_id,
                section,
                text,
                document_id,
                metadata,
                1 - (embedding <=> %s::vector) as similarity
            from chunks
            where (%s is null or metadata->>'jurisdiction' = %s)
            order by embedding <=> %s::vector
            limit %s;
        """

        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    sql,
                    (
                        vector_param,
                        jurisdiction,
                        jurisdiction,
                        vector_param,
                        top_k,
                    ),
                )
                rows = cur.fetchall()

        results: List[Tuple[PGChunk, float]] = []
        for row in rows:
            chunk = PGChunk(
                chunk_id=row["clause_id"],
                text=row["text"],
                document_id=row["document_id"],
                section=row.get("section") or "",
                metadata=row.get("metadata") or {},
            )
            sim = float(row.get("similarity") or 0.0)
            # Bound to schema expectation [0,1]
            sim = max(0.0, min(1.0, sim))
            results.append((chunk, sim))

        logger.info(f"pgvector search returned {len(results)} results")
        return results
