"""
Supabase helpers for document storage and metadata/chunk persistence.

This module intentionally centralizes all Supabase interactions so routes and
agents can remain focused on business logic.
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from uuid import uuid4

from loguru import logger
from supabase import Client, create_client

from .config import get_settings


_supabase_client: Optional[Client] = None


def _validate_supabase_config_for_pgvector() -> None:
    """
    Fail fast when pgvector mode is enabled but required Supabase settings are missing.
    """
    settings = get_settings()
    if settings.vector_store_type != "pgvector":
        return

    missing: List[str] = []
    if not settings.supabase_url:
        missing.append("SUPABASE_URL")
    if not settings.supabase_service_role_key:
        missing.append("SUPABASE_SERVICE_ROLE_KEY")
    if not settings.supabase_db_url:
        missing.append("SUPABASE_DB_URL")

    if missing:
        raise ValueError(
            "pgvector mode requires Supabase configuration. Missing: "
            + ", ".join(missing)
        )


def get_supabase_client() -> Client:
    """
    Get singleton Supabase client.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise ValueError(
            "Supabase client requested but SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY are not configured."
        )

    _supabase_client = create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )
    return _supabase_client


def upload_document_file(file_bytes: bytes, original_filename: str, document_id: str) -> str:
    """
    Upload raw file to Supabase Storage and return storage path.
    """
    settings = get_settings()
    client = get_supabase_client()

    safe_name = original_filename.replace(" ", "_")
    storage_path = f"{document_id}/{uuid4().hex}_{safe_name}"
    client.storage.from_(settings.supabase_bucket).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"upsert": "false"},
    )
    logger.info(f"Uploaded file to Supabase storage: {storage_path}")
    return storage_path


def delete_document_file(storage_path: str) -> None:
    """
    Delete file from Supabase Storage.
    """
    settings = get_settings()
    client = get_supabase_client()
    client.storage.from_(settings.supabase_bucket).remove([storage_path])
    logger.info(f"Deleted Supabase storage file: {storage_path}")


def upsert_document_record(
    document_id: str,
    filename: str,
    jurisdiction: Optional[str],
    storage_path: str,
) -> None:
    """
    Upsert documents table row.
    """
    client = get_supabase_client()
    payload = {
        "document_id": document_id,
        "filename": filename,
        "jurisdiction": jurisdiction,
        "storage_path": storage_path,
    }
    client.table("documents").upsert(payload, on_conflict="document_id").execute()


def clear_chunks_for_document(document_id: str) -> None:
    """
    Remove existing chunks for a document before re-inserting.
    """
    client = get_supabase_client()
    client.table("chunks").delete().eq("document_id", document_id).execute()


def insert_chunk_rows(rows: List[Dict[str, Any]]) -> None:
    """
    Insert chunk rows into Supabase.
    """
    if not rows:
        return
    client = get_supabase_client()
    client.table("chunks").insert(rows).execute()


def list_documents_with_chunk_counts() -> List[Dict[str, Any]]:
    """
    List documents plus chunk counts from Supabase tables.
    """
    client = get_supabase_client()
    docs_resp = client.table("documents").select("*").order("created_at", desc=True).execute()
    docs = docs_resp.data or []

    result: List[Dict[str, Any]] = []
    for d in docs:
        count_resp = (
            client.table("chunks")
            .select("id", count="exact")
            .eq("document_id", d["document_id"])
            .execute()
        )
        chunk_count = count_resp.count or 0
        result.append(
            {
                "document_id": d["document_id"],
                "filename": d.get("filename"),
                "chunk_count": chunk_count,
                "jurisdiction": d.get("jurisdiction") or "Unknown",
                "doc_type": "Unknown",
                "storage_path": d.get("storage_path"),
            }
        )
    return result


def get_document_record(document_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a single document record.
    """
    client = get_supabase_client()
    resp = client.table("documents").select("*").eq("document_id", document_id).limit(1).execute()
    data = resp.data or []
    return data[0] if data else None


def delete_document_records(document_id: str) -> int:
    """
    Delete document + chunks from Supabase DB.
    Returns deleted chunk count.
    """
    client = get_supabase_client()
    count_resp = (
        client.table("chunks")
        .select("id", count="exact")
        .eq("document_id", document_id)
        .execute()
    )
    chunk_count = count_resp.count or 0

    client.table("chunks").delete().eq("document_id", document_id).execute()
    client.table("documents").delete().eq("document_id", document_id).execute()
    return chunk_count


def validate_supabase_ready() -> None:
    """
    Public helper to validate pgvector prerequisites.
    """
    _validate_supabase_config_for_pgvector()
