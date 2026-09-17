from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Build engine kwargs based on the URL scheme
engine_kwargs = {
    "echo": False,
    "future": True,
}

# Use the converted URL from our config
db_url = settings.database_url

# For SQLite (local), we need the check_same_thread argument
if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
# For Postgres, we often need to enforce SSL in production
elif "postgresql" in db_url:
    engine_kwargs["connect_args"] = {"ssl": "require"}

engine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session