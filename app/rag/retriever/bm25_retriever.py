# Key word search (BM25)

import re
from functools import lru_cache
from langchain_community.retrievers import BM25Retriever
from sqlalchemy import select
from sqlalchemy.orm import defer
from app.config import config
from app.db import get_db_session
from app.db.models import Chunk
from app.rag.documents import chunk_to_document

# Define token pattern
_TOKEN_PATTERN = re.compile(r"[a-z0-9_]+(?:\.[a-z0-9_]+)*")

def tokenize(text: str) -> list[str]:
    return _TOKEN_PATTERN.findall(text.lower())

# Get bm25 retriever
@lru_cache(maxsize=1)
def get_bm25_retriever() -> BM25Retriever:
    with get_db_session() as session:
        stmt = select(Chunk).options(defer(Chunk.embedding))    # not loading embedding col
        docs = [chunk_to_document(c) for c in session.execute(stmt).scalars().all()]

    if not docs:
        raise RuntimeError("Bảng chunks đang rỗng - vui lòng chạy `python -m scripts.build_index` trước")

    return BM25Retriever.from_documents(
        docs,
        k=config.retriever.top_k,
        preprocess_func=tokenize,
        bm25_params={
            "k1": config.bm25.k1,
            "b": config.bm25.b
        }
    )