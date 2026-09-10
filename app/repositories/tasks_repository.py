from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.tasks import Task
from app.schemas.tasks import TaskCreate, TaskUpdate
from datetime import datetime, timedelta, timezone


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

    @staticmethod
    async def get_stats(db: AsyncSession) -> dict:
        """Get aggregated statistics about tasks"""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)

        # Total count
        total_result = await db.execute(select(func.count(Task.id)))
        total_tasks = total_result.scalar() or 0

        # Completed count
        completed_result = await db.execute(
            select(func.count(Task.id)).where(Task.completed == True)
        )
        completed_tasks = completed_result.scalar() or 0

        pending_tasks = total_tasks - completed_tasks
        completion_rate = round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0.0

        # Time-based counts
        today_result = await db.execute(
            select(func.count(Task.id)).where(Task.created_at >= today_start)
        )
        tasks_created_today = today_result.scalar() or 0

        week_result = await db.execute(
            select(func.count(Task.id)).where(Task.created_at >= week_start)
        )
        tasks_created_this_week = week_result.scalar() or 0

        month_result = await db.execute(
            select(func.count(Task.id)).where(Task.created_at >= month_start)
        )
        tasks_created_this_month = month_result.scalar() or 0

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": completion_rate,
            "tasks_created_today": tasks_created_today,
            "tasks_created_this_week": tasks_created_this_week,
            "tasks_created_this_month": tasks_created_this_month,
        }