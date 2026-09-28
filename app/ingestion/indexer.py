# Parse index each doc
# Insert/Update docs + chunks into database

from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.db import get_db_session
from app.db.models import Document, Chunk
from app.embedding import get_embedder
from app.ingestion.chunker import ChunkDraft
from app.observability.logger import get_logger

logger = get_logger(__name__)

# Upsert: Decide whether this doc need to be re-chunked (new, changed, not changed)
def upsert_document(source: str, url: str, title: str, page_content_hash: str, crawled_at: datetime) -> tuple[int, bool]:
    """If doc doesn't change => False else True"""
    with get_db_session() as session:
        existing = session.execute(select(Document).where(Document.url == url)).scalar_one_or_none()

        # If it's new
        if existing is None:
            doc = Document(
                source=source,
                url=url,
                title=title,
                page_content_hash=page_content_hash,
                crawled_at=crawled_at,
                need_reindex=True
            )
            session.add(doc)
            session.commit()
            session.refresh(doc)
            logger.info(f"Document mới: {url}")
            return doc.id, True

        # If it's changed
        if existing.page_content_hash != page_content_hash:
            # Delete old chunk
            session.query(Chunk).filter(Chunk.document_id == existing.id).delete()
            existing.page_content_hash = page_content_hash
            existing.crawled_at = crawled_at
            existing.need_reindex = True
            session.commit()
            logger.info(f"Document đã thay đổi, xóa các chunk cũ: {url}")
            return existing.id, True

        if existing.need_reindex:
            logger.info(f"Document chưa index xong, sẽ retry: {url}")
            return existing.id, True

        logger.debug(f"Document không thay đổi, bỏ qua: {url}")
        return existing.id, False
        
# Mark document indexed
def mark_document_indexed(document_id: int) -> None:
    """Mark document which is indexed"""
    with get_db_session() as session:
        doc = session.get(Document, document_id)
        doc.last_indexed_at = datetime.now(UTC)
        doc.need_reindex = False
        session.commit() 

# Insert: embed batch + insert, auto dedup by content_hash
def insert_chunks(document_id: int, chunk_drafts: list[ChunkDraft]) -> int:
    """Embed by batch"""
    if not chunk_drafts:
        return 0

    # A document can produce identical chunks; content_hash is globally unique.
    unique_drafts = []
    seen_hashes = set()
    for draft in chunk_drafts:
        if draft.content_hash not in seen_hashes:
            unique_drafts.append(draft)
            seen_hashes.add(draft.content_hash)

    with get_db_session() as session:
        existing_hashes = {
            row[0] for row in session.execute(
                select(Chunk.content_hash).where(
                    Chunk.content_hash.in_([c.content_hash for c in unique_drafts])
                )
            )
        }

        drafts_to_insert = [
            draft for draft in unique_drafts
            if draft.content_hash not in existing_hashes
        ]
        embeddings = get_embedder().embed_documents([c.content for c in drafts_to_insert])
        inserted = 0
        for draft, embedding in zip(drafts_to_insert, embeddings):
            session.add(Chunk(
                document_id=document_id,
                source=draft.source, 
                url=draft.url, 
                title=draft.title,
                section_heading=draft.section_heading, 
                heading_path=draft.heading_path,
                chunk_index=draft.chunk_index, 
                content=draft.content,
                token_count=draft.token_count, 
                embedding=embedding,
                content_hash=draft.content_hash,
            ))
            inserted += 1

        session.commit()
    return inserted
