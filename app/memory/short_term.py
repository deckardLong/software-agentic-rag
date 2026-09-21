# Manage short term memory

from datetime import datetime, timedelta, timezone
from sqlalchemy import select, delete
from app.db import get_db_session
from app.db.models import ConversationShortTerm
from app.config import config
from app.observability.logger import get_logger

logger = get_logger(__name__)

# Save short term turn
def save_short_term_turn(session_id: str, trace_id: str, 
                         turn_index: int, user_query: str, final_answer: str) -> None:
    """Save 1 turn question - answer"""
    ttl_hours = config.memory.short_term_ttl_hours
    expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)    # auto set expired time

    # Save to database
    with get_db_session() as session:
        row = ConversationShortTerm(
            session_id=session_id,
            trace_id=trace_id,
            turn_index=turn_index,
            user_query=user_query,
            final_answer=final_answer,
            expires_at=expires_at
        )
        session.add(row)
        session.commit()
    logger.info(f"Short-term turn đã được lưu: session = {session_id}, turn = {turn_index}")

# Get recent short term
def get_recent_short_term(session_id: str) -> list[dict]:
    """Get all question - answer turn recently with not expired """
    max_turns = config.memory.short_term_max_turns   # get max turns
    now = datetime.now(timezone.utc)

    with get_db_session() as session:
        stmt = (
            select(ConversationShortTerm)
            .where(ConversationShortTerm.session_id == session_id)
            .where(ConversationShortTerm.expires_at > now)
            .order_by(ConversationShortTerm.turn_index.desc())
            .limit(max_turns)
        )
        rows = session.execute(stmt).scalars().all()  # get the list of rows
        return [
            {
                "query": row.user_query,
                "answer": row.final_answer,
                "timestamp": row.created_at.isoformat()
            }
            for row in reversed(rows)
        ]

# Delete expired short term
def delete_expired_short_term() -> int:
    """Delete all expired rows"""
    now = datetime.now(timezone.utc)
    with get_db_session() as session:
        result = session.execute(
            delete(ConversationShortTerm).where(ConversationShortTerm.expires_at <= now)    # execute delete rows
        )
        session.commit()
        deleted_count = result.rowcount

    logger.info(f"Đã xóa {deleted_count} hàng bộ nhớ short-term hết hạn (expired)")
    return deleted_count