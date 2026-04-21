"""
FastAPI application - REST API for Legal RAG system.

Endpoints:
- POST /api/documents/upload - Upload and ingest documents
- GET /api/documents - List all documents
- DELETE /api/documents/{doc_id} - Delete a document
- POST /api/query - Submit a legal query
- GET /api/stats - Get system statistics
"""

from .main import create_app

__all__ = ["create_app"]
