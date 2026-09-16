"""
Seed the database with realistic fake tasks for a specific user.

Usage:
    poetry run python -m scripts.seed_data 10000
    poetry run python -m scripts.seed_data 10000 --email you@example.com

If no --email is given, it defaults to the first user in the database.
"""
import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd
from faker import Faker
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.tasks import Task
from app.models.users import User

fake = Faker()


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
        days_ago = random.randint(0, 90)
        created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
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

    df["week"] = df["created_at"].dt.isocalendar().week
    weekly = df.groupby("week").size()
    print(f"   Busiest week:   Week {weekly.idxmax()} with {weekly.max()} tasks")


async def get_target_user(session, email: str | None) -> User:
    """Find the user to attach tasks to. If no email given, use first user in DB."""
    if email:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
    else:
        result = await session.execute(select(User).order_by(User.id).limit(1))
        user = result.scalar_one_or_none()

    if user is None:
        raise RuntimeError(
            "No user found! Register a user first via POST /auth/register, "
            "or pass --email of an existing user."
        )
    return user


async def seed_database(count: int, email: str | None) -> None:
    """Insert the generated tasks into the database for a specific user."""
    async with AsyncSessionLocal() as session:
        user = await get_target_user(session, email)
        print(f"\n👤 Seeding tasks for user: {user.email} (id={user.id})")

        print(f"\n🎲 Generating {count} fake tasks...")
        df = generate_tasks_data(count)
        analyze_data(df)

        print(f"\n💾 Inserting into database (bulk insert)...")
        task_objects = [
            Task(
                title=row["title"],
                description=row["description"],
                completed=bool(row["completed"]),
                created_at=row["created_at"],
                user_id=user.id,
            )
            for _, row in df.iterrows()
        ]
        session.add_all(task_objects)
        await session.commit()

    print(f"✅ Successfully inserted {count} tasks for {user.email}!\n")


def parse_args() -> tuple[int, str | None]:
    """Parse CLI args: count and optional --email."""
    args = sys.argv[1:]

    email = None
    if "--email" in args:
        idx = args.index("--email")
        if idx + 1 >= len(args):
            print("❌ --email requires a value")
            sys.exit(1)
        email = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    count = int(args[0]) if args else 1000

    return count, email


if __name__ == "__main__":
    count, email = parse_args()
    asyncio.run(seed_database(count, email))