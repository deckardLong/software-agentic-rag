# Setup PostgreSQL - Create extension pgvector & tables & HNSW index for all vector cols

from sqlalchemy import text
from app.db import engine, Base
import app.db.models
from app.observability import setup_logging, get_logger

# Setup logger
setup_logging()
logger = get_logger(__name__)

# Create extension
def create_extension():
    logger.info("Đang kích hoạt gói tiện ích mở rộng pgvector...")
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    logger.info("Gói mở rộng pgvector đã sẵn sàng.")

# Create tables
def create_tables():
    logger.info("Đang tạo các bảng từ các model SQLAlchemy...")
    Base.metadata.create_all(bind=engine)
    logger.info(f"Danh sách các bảng đã được tạo: {list(Base.metadata.tables.keys())}")

# Create vector indexes
def create_vector_indexes():
    """Create HNSW indexes"""
    logger.info("Đang khởi tạo các index HNSW cho các cột vector...")
    statements = [
        """
        CREATE INDEX IF NOT EXISTS idx_chunks_embedding
        ON chunks USING hnsw (embedding vector_cosine_ops);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_long_term_embedding
        ON conversation_long_term USING hnsw (embedding vector_cosine_ops);
        """,
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_chunks_content_hash
        ON chunks(content_hash);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_documents_needs_reindex
        ON documents(need_reindex) WHERE need_reindex = TRUE;
        """ 
    ]
    with engine.connect() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        conn.commit()
    logger.info("Các index của các vector đã sẵn sàng.")

# Verify setup
def verify_setup():
    logger.info("Đang xác minh cài đặt...")
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        ))
        tables = [row[0] for row in result]
        logger.info(f"Các bảng trong database: {tables}")

        ext_result = conn.execute(text(
            "SELECT extname FROM pg_extension WHERE extname = 'vector';"
        ))
        has_vector_ext = ext_result.fetchone() is not None
        logger.info(f"Tiện ích pgvector đã được bật: {has_vector_ext}")

        expected_tables = {
            "documents", "chunks", "conversation_short_term",
            "conversation_long_term", "query_log", "retrieval_log"
        }
        # Check if any table missing
        missing = expected_tables - set(tables)
        if missing:
            logger.warning(f"Mất bảng: {missing}")
        else:
            logger.info("Các bảng đã tồn tại đầy đủ.")

def main():
    logger.info("===== Quá trình cài đặt PostgreSQL bắt đầu =====")
    create_extension()
    create_tables()
    create_vector_indexes()
    verify_setup()
    logger.info("===== Quá trình cài đặt PostgreSQL kết thúc =====")

if __name__ == "__main__":
    main()
