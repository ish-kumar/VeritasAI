"""
FastAPI Application - Main entry point.

This creates the FastAPI app with all routes and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .routes import documents, query, stats


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Why this pattern:
    - Factory function (can create multiple instances)
    - Clean separation of concerns
    - Easy to test
    - Configurable
    """
    app = FastAPI(
        title="Legal RAG API",
        description="Production-grade Legal RAG system with adversarial reasoning",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )
    
    # CORS middleware (allow frontend to call API)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
    app.include_router(query.router, prefix="/api/query", tags=["query"])
    app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
    
    # Health check endpoint
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "legal-rag-api"}
    
    logger.info("FastAPI application created")
    
    return app
