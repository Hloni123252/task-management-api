"""
Seed the database with realistic fake tasks.

Usage:
    poetry run python -m scripts.seed_data 10000
    (The number is how many tasks to generate. Default: 1000)
"""
import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd
from faker import Faker

from app.core.database import AsyncSessionLocal
from app.models.tasks import Task

fake = Faker()


# Realistic task templates
TASK_TEMPLATES = [
    "Review {} pull request",
    "Fix bug in {} module",
    "Write tests for {}",
    "Deploy {} to production",
    "Refactor {} service",
    "Update documentation for {}",
    "Optimize {} query performance",
    "Add logging to {} endpoint",
    "Investigate {} error report",
    "Migrate {} to new database",
    "Design {} API endpoint",
    "Benchmark {} performance",
]

MODULES = [
    "user", "auth", "payment", "notification", "search", "analytics",
    "reporting", "admin", "profile", "settings", "order", "inventory",
    "billing", "shipping", "catalog", "cart", "checkout", "review",
]


def generate_tasks_data(count: int) -> pd.DataFrame:
    """Generate fake task data using Faker, return as Pandas DataFrame."""
    tasks = []

    for _ in range(count):
        # Random creation date in the last 90 days
        days_ago = random.randint(0, 90)
        created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)

        # 65% chance of being completed
        completed = random.random() < 0.65

        tasks.append({
            "title": random.choice(TASK_TEMPLATES).format(random.choice(MODULES)),
            "description": fake.sentence(nb_words=12),
            "completed": completed,
            "created_at": created_at,
        })

    return pd.DataFrame(tasks)


def analyze_data(df: pd.DataFrame) -> None:
    """Print a quick analysis of the generated data using Pandas."""
    print("\n📊 Data Analysis (using Pandas):")
    print(f"   Total tasks:    {len(df)}")
    print(f"   Completed:      {df['completed'].sum()} ({df['completed'].mean() * 100:.1f}%)")
    print(f"   Pending:        {(~df['completed']).sum()}")
    print(f"   Date range:     {df['created_at'].min().date()} -> {df['created_at'].max().date()}")

    # Tasks per week (a quick time-series insight)
    df["week"] = df["created_at"].dt.isocalendar().week
    weekly = df.groupby("week").size()
    print(f"   Busiest week:   Week {weekly.idxmax()} with {weekly.max()} tasks")


async def seed_database(count: int) -> None:
    """Insert the generated tasks into the database."""
    print(f"\n🎲 Generating {count} fake tasks...")
    df = generate_tasks_data(count)

    analyze_data(df)

    print(f"\n💾 Inserting into database (bulk insert)...")

    async with AsyncSessionLocal() as session:
        # Bulk insert for performance
        task_objects = [
            Task(
                title=row["title"],
                description=row["description"],
                completed=bool(row["completed"]),
                created_at=row["created_at"],
            )
            for _, row in df.iterrows()
        ]

        session.add_all(task_objects)
        await session.commit()

    print(f"✅ Successfully inserted {count} tasks!\n")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    asyncio.run(seed_database(count))