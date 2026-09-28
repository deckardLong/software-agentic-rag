# Run pipeline ingestion: Read raw files -> upsert docs -> chunk -> embed + insert

import argparse
import json
from datetime import datetime
from pathlib import Path
from app.ingestion.chunker import chunk_document_dispatch
from app.ingestion.indexer import upsert_document, insert_chunks, mark_document_indexed
from app.observability import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

RAW_DATA_DIR = Path("data/raw")

# Process src files
def process_source_file(jsonl_path: Path) -> dict:
    source = jsonl_path.stem    # "redis.jsonl" -> "redis"
    stats = {
        "documents_processed": 0,
        "documents_skipped": 0,
        "chunks_inserted": 0
    }
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            url = record["url"]
            title = record.get("title", "")
            content_markdown = record["content_markdown"]
            page_content_hash = record["content_hash"]
            crawled_at = datetime.fromisoformat(record["crawled_at"])

            # Get doc, need reindex?
            document_id, needs_reindex = upsert_document(
                source=source,
                url=url,
                title=title,
                page_content_hash=page_content_hash,
                crawled_at=crawled_at
            )

            # If not reindex => Skip
            if not needs_reindex:
                stats["documents_skipped"] += 1
                continue

            chunk_drafts = chunk_document_dispatch(source, url, title, content_markdown)
            inserted = insert_chunks(document_id, chunk_drafts)

            # Mark as indexed
            mark_document_indexed(document_id)

            stats["documents_processed"] += 1
            stats["chunks_inserted"] += inserted
            logger.info(f"[{source}] Đã được index: {url} -> {inserted} chunks")
    return stats

# Main
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, default=None, help="Chỉ build một nguồn cụ thể, ví dụ như 'redis'")
    args = parser.parse_args()

    # Check if raw data doesn't exist
    if not RAW_DATA_DIR.exists():
        logger.error(f"Không tìm thấy thư mục raw data: {RAW_DATA_DIR}")
        return

    jsonl_files = (
        [RAW_DATA_DIR / f"{args.source}.jsonl"] if args.source
        else sorted(RAW_DATA_DIR.glob("*.jsonl"))
    )

    # Total stats
    total_stats = {
        "documents_processed": 0,
        "documents_skipped": 0,
        "chunks_inserted": 0
    }

    for jsonl_path in jsonl_files:
        if not jsonl_path.exists():
            logger.warning(f"File không tồn tại, bỏ qua: {jsonl_path}")
            continue

        logger.info(f"===== Đang xử lý {jsonl_path.name} =====")
        stats = process_source_file(jsonl_path)

        for k in total_stats:
            total_stats[k] += stats[k]

    logger.info(f"===== Quá trình build index thành công =====")

if __name__ == "__main__":
    main()