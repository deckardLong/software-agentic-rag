# Chunking docs

import hashlib
from dataclasses import dataclass
from urllib.parse import urlparse
from app.ingestion.markdown_cleaner import clean_markdown, is_translated_page
from app.ingestion.heading_splitter import split_by_heading
from app.ingestion.recursive_splitter import split_long_section
from app.ingestion.token_counter import count_tokens, exceeds_safe_cap

# Define dataclass
@dataclass
class ChunkDraft:
    source: str
    url: str
    title: str
    section_heading: str
    heading_path: str
    chunk_index: int
    content: str
    token_count: int
    content_hash: str

# Hash content
def _hash_content(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]    # avoid saving all text => Save hash content to be faster and more readable

# Chunk doc
def chunk_document(source: str, url: str, title: str, raw_markdown: str) -> list[ChunkDraft]:
    url_path = urlparse(url).path
    if is_translated_page(url_path):
        return []   # skip if it's translated page

    # Clean markdown
    cleaned = clean_markdown(raw_markdown)
    if not cleaned:
        return []
    sections = split_by_heading(cleaned) or [
        {
            "content": cleaned,
            "heading_path": [],
            "immediate_heading": ""
        }
    ]

    drafts: list[ChunkDraft] = []
    chunk_index = 0

    for section in sections:
        heading_path_str = " > ".join(section["heading_path"])
        prefix = f"# {title}\n" + (f"## {heading_path_str}\n\n" if heading_path_str else "\n")
        full_content = prefix + section["content"]

        sub_chunks = (
            [full_content] if not exceeds_safe_cap(full_content) else split_long_section(full_content)
        )

        for sub_chunk_text in sub_chunks:
            drafts.append(ChunkDraft(
                source=source, 
                url=url, 
                title=title,
                section_heading=section["immediate_heading"],
                heading_path=heading_path_str,
                chunk_index=chunk_index,
                content=sub_chunk_text,
                token_count=count_tokens(sub_chunk_text),
                content_hash=_hash_content(sub_chunk_text)
            ))
            chunk_index += 1
    return drafts

# Chunk by route (Redis & Other chunks)
def chunk_document_dispatch(source: str, url: str, title: str, raw_markdown: str) -> list[ChunkDraft]:
    """Chunk by route"""

    # Redis
    if source == "redis":
        from app.ingestion.redis_chunker import chunk_redis_document
        return chunk_redis_document(url, title, raw_markdown)

    # Other chunks
    return chunk_document(source, url, title, raw_markdown)