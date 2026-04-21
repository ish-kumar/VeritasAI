"""
Legal Document Chunker - Clause-aware chunking for legal documents.

Design philosophy: Respect document structure.

Why this matters for legal RAG:
- Don't split clauses mid-sentence
- Preserve section headers
- Keep related content together
- Generate stable chunk IDs for citation verification

Chunking strategy:
1. Detect section headers (e.g., "Section 12.3", "Article V")
2. Split on natural boundaries (paragraphs, clauses)
3. Maintain overlap for context
4. Generate unique, stable IDs
"""

from typing import List, Optional
from pydantic import BaseModel, Field
import re
import hashlib

from loguru import logger


class DocumentChunk(BaseModel):
    """
    A chunk of a legal document.
    
    Why these fields:
    - chunk_id: Unique, stable identifier (for citation verification)
    - text: The actual chunk content
    - document_id: Link back to source document
    - section: Human-readable section info
    - start_char: Character offset in original document
    - end_char: End offset (for highlighting)
    - metadata: Additional context (jurisdiction, doc type, etc.)
    
    Design decision: chunk_id is hash-based
    - Deterministic (same text → same ID)
    - Unique (different text → different ID)
    - Stable across re-ingestion
    """
    chunk_id: str = Field(..., description="Unique chunk identifier")
    text: str = Field(..., description="Chunk text content")
    document_id: str = Field(..., description="Source document identifier")
    section: str = Field(default="", description="Section header or number")
    start_char: int = Field(..., description="Start position in original document")
    end_char: int = Field(..., description="End position in original document")
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata (jurisdiction, doc_type, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "DOC1_CHUNK_a3f9e8b2",
                "text": "Section 12.3 - Dispute Resolution. Any dispute arising under this Agreement...",
                "document_id": "DOC1",
                "section": "Section 12.3 - Dispute Resolution",
                "start_char": 15420,
                "end_char": 15892,
                "metadata": {"jurisdiction": "California", "doc_type": "employment_agreement"}
            }
        }


class LegalChunker:
    """
    Chunks legal documents with clause-aware splitting.
    
    Strategy:
    1. Detect section headers
    2. Split into paragraphs
    3. Combine into chunks (respect size limits)
    4. Add overlap for context
    5. Generate stable IDs
    
    Why not just split every N tokens:
    - Breaks clauses mid-sentence
    - Loses structural context
    - Citations become meaningless
    
    Why clause-aware chunking:
    - Preserves legal meaning
    - Each chunk is self-contained
    - Citations map to real clauses
    """
    
    # Section header patterns (common in legal documents)
    SECTION_PATTERNS = [
        r'^(?:SECTION|Section|SEC\.|Sec\.)\s+(\d+(?:\.\d+)*)',  # "Section 12.3"
        r'^(?:ARTICLE|Article|ART\.|Art\.)\s+([IVXLCDM]+|\d+)',  # "Article V"
        r'^(\d+(?:\.\d+)*)\s+[A-Z]',  # "12.3 DISPUTE RESOLUTION"
        r'^\s*§\s*(\d+(?:\.\d+)*)',  # "§ 12.3"
    ]
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100,
    ):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Target chunk size in tokens (approx)
            chunk_overlap: Overlap between chunks in tokens
            min_chunk_size: Minimum chunk size (don't create tiny chunks)
        
        Why these defaults:
        - 500 tokens: ~1-2 paragraphs, fits typical clause
        - 50 token overlap: Maintains context across chunks
        - 100 token min: Avoids tiny, meaningless chunks
        
        Learning insight: Legal documents have variable clause lengths
        - Some clauses are 50 tokens (short)
        - Some are 1000+ tokens (long definitions)
        - We adapt to the content
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
        # Compile regex patterns for efficiency
        self.section_regexes = [
            re.compile(pattern, re.MULTILINE)
            for pattern in self.SECTION_PATTERNS
        ]
    
    def chunk_document(
        self,
        text: str,
        document_id: str,
        metadata: Optional[dict] = None
    ) -> List[DocumentChunk]:
        """
        Chunk a legal document into semantic chunks.
        
        Args:
            text: Full document text
            document_id: Unique identifier for the document
            metadata: Additional metadata to attach to chunks
            
        Returns:
            List of DocumentChunk objects
            
        Algorithm:
        1. Detect sections
        2. Split into paragraphs
        3. Group paragraphs into chunks (respect size limits)
        4. Add overlap
        5. Generate IDs
        
        Why this approach:
        - Preserves document structure
        - Chunks are meaningful units
        - Stable IDs for citations
        """
        if not text or not text.strip():
            logger.warning(f"Empty document: {document_id}")
            return []
        
        metadata = metadata or {}
        
        logger.info(
            f"Chunking document {document_id}: "
            f"{len(text)} chars, target size {self.chunk_size} tokens"
        )
        
        # Split into sections
        sections = self._detect_sections(text)
        
        # Split each section into chunks
        all_chunks = []
        char_offset = 0
        
        for section_idx, (section_header, section_text) in enumerate(sections):
            section_chunks = self._chunk_section(
                section_text=section_text,
                section_header=section_header,
                document_id=document_id,
                start_offset=char_offset,
                metadata=metadata
            )
            
            all_chunks.extend(section_chunks)
            char_offset += len(section_text)
        
        logger.success(
            f"Created {len(all_chunks)} chunks from {len(sections)} sections"
        )
        
        return all_chunks
    
    def _detect_sections(self, text: str) -> List[tuple[str, str]]:
        """
        Detect sections in the document.
        
        Returns:
            List of (section_header, section_text) tuples
            
        Strategy:
        - Find all section headers using regex patterns
        - Split text at section boundaries
        - If no sections found, treat whole doc as one section
        
        Why detect sections:
        - Legal documents are hierarchical
        - Sections are natural chunking boundaries
        - Preserves document structure
        """
        # Find all section headers and their positions
        section_matches = []
        
        for regex in self.section_regexes:
            for match in regex.finditer(text):
                section_matches.append((
                    match.start(),
                    match.group(0),  # Full matched text (the header)
                ))
        
        # Sort by position
        section_matches.sort(key=lambda x: x[0])
        
        if not section_matches:
            # No sections found, treat whole doc as one section
            return [("Document", text)]
        
        # Split text at section boundaries
        sections = []
        
        for i, (pos, header) in enumerate(section_matches):
            # Find where this section ends (start of next section or end of doc)
            if i + 1 < len(section_matches):
                end_pos = section_matches[i + 1][0]
            else:
                end_pos = len(text)
            
            section_text = text[pos:end_pos]
            sections.append((header.strip(), section_text.strip()))
        
        # Handle text before first section (preamble)
        if section_matches[0][0] > 0:
            preamble = text[:section_matches[0][0]].strip()
            if preamble:
                sections.insert(0, ("Preamble", preamble))
        
        return sections
    
    def _chunk_section(
        self,
        section_text: str,
        section_header: str,
        document_id: str,
        start_offset: int,
        metadata: dict
    ) -> List[DocumentChunk]:
        """
        Chunk a single section into smaller pieces.
        
        Strategy:
        1. Split section into paragraphs
        2. Group paragraphs into chunks (respect size)
        3. Add overlap between chunks
        4. Generate chunk IDs
        """
        # Split into paragraphs (try double newline first, fall back to single)
        paragraphs = [p.strip() for p in section_text.split('\n\n') if p.strip()]
        
        # If no paragraphs with double newline, try single newline
        if not paragraphs:
            paragraphs = [p.strip() for p in section_text.split('\n') if p.strip()]
        
        # If still no paragraphs, treat entire section as one paragraph
        if not paragraphs and section_text.strip():
            paragraphs = [section_text.strip()]
        
        if not paragraphs:
            return []
        
        chunks = []
        current_chunk_text = []
        current_chunk_tokens = 0
        chunk_start_char = start_offset
        
        for para_idx, para in enumerate(paragraphs):
            para_tokens = self._estimate_tokens(para)
            
            # Check if adding this paragraph exceeds chunk size
            if current_chunk_tokens + para_tokens > self.chunk_size and current_chunk_text:
                # Create chunk from accumulated paragraphs
                chunk_text = "\n\n".join(current_chunk_text)
                chunk_end_char = chunk_start_char + len(chunk_text)
                
                chunk = self._create_chunk(
                    text=chunk_text,
                    document_id=document_id,
                    section=section_header,
                    start_char=chunk_start_char,
                    end_char=chunk_end_char,
                    metadata=metadata
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                # Keep last paragraph for context
                if len(current_chunk_text) > 1:
                    overlap_text = current_chunk_text[-1]
                    current_chunk_text = [overlap_text, para]
                    current_chunk_tokens = self._estimate_tokens(overlap_text) + para_tokens
                    chunk_start_char = chunk_end_char - len(overlap_text) - 2  # -2 for \n\n
                else:
                    current_chunk_text = [para]
                    current_chunk_tokens = para_tokens
                    chunk_start_char = chunk_end_char
            else:
                # Add paragraph to current chunk
                current_chunk_text.append(para)
                current_chunk_tokens += para_tokens
        
        # Create final chunk if any text remains
        if current_chunk_text:
            chunk_text = "\n\n".join(current_chunk_text)
            
            # Create chunk even if below minimum size (for small sections)
            # Better to have small chunks than no chunks
            chunk_end_char = chunk_start_char + len(chunk_text)
            
            chunk = self._create_chunk(
                text=chunk_text,
                document_id=document_id,
                section=section_header,
                start_char=chunk_start_char,
                end_char=chunk_end_char,
                metadata=metadata
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(
        self,
        text: str,
        document_id: str,
        section: str,
        start_char: int,
        end_char: int,
        metadata: dict
    ) -> DocumentChunk:
        """
        Create a DocumentChunk with a stable ID.
        
        Chunk ID format: {document_id}_CHUNK_{hash}
        
        Why hash-based IDs:
        - Deterministic (same text → same ID)
        - Unique (collision probability ~0)
        - Stable across re-ingestion
        - No need for database sequence
        
        Hash algorithm: MD5 (fast, good enough for our use case)
        - Not for security (no crypto needed)
        - Just need uniqueness
        """
        # Generate stable chunk ID from content
        content_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
        chunk_id = f"{document_id}_CHUNK_{content_hash}"
        
        return DocumentChunk(
            chunk_id=chunk_id,
            text=text,
            document_id=document_id,
            section=section,
            start_char=start_char,
            end_char=end_char,
            metadata=metadata
        )
    
    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        Estimate token count from text.
        
        Rule of thumb: 1 token ≈ 4 characters (for English)
        
        Why estimate:
        - Fast (no tokenizer needed)
        - Good enough for chunking
        - Actual token count varies by model
        
        For production:
        - Could use tiktoken for OpenAI models
        - Could use model-specific tokenizer
        - But estimation is usually sufficient
        """
        return len(text) // 4
