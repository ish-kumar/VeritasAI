"""
Document ingestion pipeline.

Handles:
- Document parsing (PDF, DOCX, TXT)
- Chunking (clause-aware for legal documents)
- Embedding generation
- Vector store indexing
"""

from .document_parser import DocumentParser, ParsedDocument
from .chunker import LegalChunker, DocumentChunk
from .embedder import EmbeddingGenerator
from .pipeline import IngestionPipeline

__all__ = [
    "DocumentParser",
    "ParsedDocument",
    "LegalChunker",
    "DocumentChunk",
    "EmbeddingGenerator",
    "IngestionPipeline",
]
