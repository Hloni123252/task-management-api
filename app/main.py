from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.api.v1.endpoints import tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created (or already exist)")
    yield
    await engine.dispose()
    print("✅ Database connection closed")

app = FastAPI(
    title="Task Management API",
    version="0.1.0",
    description="Production-grade backend with analytics",
    lifespan=lifespan,
)

# Register the task routes
app.include_router(tasks.router)

@app.get("/")
async def root():
    return {"message": "Task API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "database": "connected"}