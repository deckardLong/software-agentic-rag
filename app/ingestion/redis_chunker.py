# Redis topic chunking (API Redis has already split sections) => 1 section = 1 chunk

import hashlib
from app.ingestion.markdown_cleaner import clean_markdown, is_translated_page
from app.ingestion.heading_splitter import split_by_heading
from app.ingestion.recursive_splitter import split_long_section
from app.ingestion.token_counter import count_tokens, exceeds_safe_cap
from app.ingestion.chunker import ChunkDraft
from urllib.parse import urlparse

# Hash content
def _hash_content(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]

# Chunk Redis docs
def chunk_redis_document(url: str, title: str, raw_markdown: str) -> list[ChunkDraft]:
    # Get URL path
    url_path = urlparse(url).path

    # Check whether it's translated page
    if is_translated_page(url_path):
        return []

    # Check whether it't markdown
    cleaned = clean_markdown(raw_markdown)
    if not cleaned:
        return []

    sections = split_by_heading(cleaned) or [
        {
            "content": cleaned,
            "heading_path": [],
            "immediate_heading": []
        }
    ]
    drafts: list[ChunkDraft] = []
    chunk_index = 0

    for section in sections:
        heading_path_str = " > ".join(section["heading_path"])
        prefix =  f"# {title}\n" + (f"## {heading_path_str}\n\n" if heading_path_str else "\n")
        full_content = prefix + section["content"]

        # Get sub-chunks
        sub_chunks = (
            [full_content]
            if not exceeds_safe_cap(full_content)
            else split_long_section(full_content, chunk_overlap=0)
        )

        # Get src, URL, title,...
        for sub_chunk_text in sub_chunks:
            drafts.append(ChunkDraft(   
                source="redis", 
                url=url, 
                title=title,
                section_heading=section["immediate_heading"],
                heading_path=heading_path_str,
                chunk_index=chunk_index,
                content=sub_chunk_text,
                token_count=count_tokens(sub_chunk_text),
                content_hash=_hash_content(sub_chunk_text),
            ))
            chunk_index += 1

    return drafts    