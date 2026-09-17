from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Core settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    
    # Redis (kept for future use)
    REDIS_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def database_url(self) -> str:
        """
        Convert common Postgres URL schemes to one compatible with asyncpg.
        
        Render and many other providers give `postgres://` URLs, but SQLAlchemy
        with asyncpg requires `postgresql+asyncpg://`.
        """
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

settings = Settings()