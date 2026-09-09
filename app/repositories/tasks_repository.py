from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tasks import Task
from app.schemas.tasks import TaskCreate, TaskUpdate

class TaskRepository:
    @staticmethod
    async def create(db: AsyncSession, task_data: TaskCreate) -> Task:
        db_task = Task(**task_data.model_dump())
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(Task).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, task_id: int) -> Task | None:
        result = await db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(db: AsyncSession, task_id: int, task_data: TaskUpdate) -> Task | None:
        db_task = await TaskRepository.get_by_id(db, task_id)
        if db_task:
            update_data = task_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_task, key, value)
            await db.commit()
            await db.refresh(db_task)
        return db_task

    @staticmethod
    async def delete(db: AsyncSession, task_id: int) -> bool:
        db_task = await TaskRepository.get_by_id(db, task_id)
        if db_task:
            await db.delete(db_task)
            await db.commit()
            return True
        return False