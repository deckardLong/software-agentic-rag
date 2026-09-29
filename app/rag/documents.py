# Convert format to documents and then dict for framework LangChain

from langchain_core.documents import Document

# Chunk to Document
def chunk_to_document(chunk, vector_score: float | None = None) -> Document:
    """Chunk to Document for LangChain"""
    metadata = {
        "chunk_id": chunk.id,
        "source": chunk.source,
        "url": chunk.url,
        "title": chunk.title,
        "heading_path": chunk.heading_path,
        "section_heading": chunk.section_heading,
        "chunk_index": chunk.chunk_index,
        "token_count": chunk.token_count 
    }

    # Get score
    if vector_score is not None:
        metadata["vector_score"] = round(vector_score, 4)
    return Document(
        page_content=chunk.content,
        metadata=metadata
    )

# Document to Dict
def doc_to_dict(doc: Document) -> dict:
    """Document to Dict (Serialize)"""
    return {
        "content": doc.page_content,
        **doc.metadata
    }
