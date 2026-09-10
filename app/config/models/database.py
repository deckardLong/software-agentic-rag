# Create database config object

from pydantic import BaseModel

class PostgreSQLConfig(BaseModel):
    """PostgreSQL + pgvector configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "agentic_rag_db"
    user: str = "postgres"
    password: str 
    pool_size: int = 5
    max_overflow: int = 10  # the maximum number of connections if all pool is busy
    pool_timeout: int = 30  # timeout when after 30s there is no pool free

    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"