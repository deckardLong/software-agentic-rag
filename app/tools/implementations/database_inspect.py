# Define database inspect for understanding the data of the system

from sqlalchemy import inspect, text
from pydantic import BaseModel, Field
from typing import Literal, Optional
from app.db import engine

# Max rows
MAX_SAMPLE_ROWS = 5

# Define class
class DatabaseInspectArgs(BaseModel):
    operation: Literal["list_tables", "describe_table", "row_count", "sample_rows"] = Field(
        description="list_tables: liệt kê bảng; describe_table: xem cột+kiểu dữ liệu; "
                    "row_count: đếm số dòng; sample_rows: xem tối đa 5 dòng mẫu"
    )
    table_name: Optional[str] = Field(default=None, description="Bắt buộc với mọi operation trừ list_tables")

# Define valid tables
def _valid_tables() -> set[str]:
    return set(inspect(engine).get_table_names())

# Inspect database
def inspect_database(operation: str, table_name: str | None = None) -> dict:
    """Check database tool"""
    inspector = inspect(engine)

    # List tables
    if operation == "list_tables":
        return {
            "tables": inspector.get_table_names()
        }

    if not table_name:
        return {
            "error": "table_name là bắt buộc đối với operation này"
        }

    # Valid tables
    valid_tables = _valid_tables()

    if table_name not in valid_tables:
        return {
            "error": f"Bảng '{table_name}' không tồn tại. Các bảng hợp lệ: {sorted(valid_tables)}"
        }

    # Describe table
    if operation == "describe_table":
        columns = inspector.get_columns(table_name)
        return {
            "table": table_name,
            "columns": [{
                "name": c["name"], 
                "type": str(c["type"])
            } for c in columns]
        }

    # Row count
    if operation == "row_count":
        with engine.connect() as conn:
            count = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar_one()
        return {
            "table": table_name,
            "row_count": count
        }

    # Sample rows
    if operation == "sample_rows":
        with engine.connect() as conn:
            rows = conn.execute(text(f'SELECT * FROM "{table_name}" LIMIT {MAX_SAMPLE_ROWS}')).mappings().all()
        return {
            "table": table_name,
            "sample_rows": [dict[r] for r in rows]
        }

    return {
        "error": f"Operation không hợp lệ: {operation}"
    }
    