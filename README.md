# Task Management API

> A production-grade, multi-tenant REST API with JWT authentication and analytics — built with FastAPI, SQLAlchemy 2.0, and async Python.

🌐 **Live Demo:** https://task-management-api-m5rq.onrender.com/docs
>
> ℹ️ Free tier may take 30 seconds on first request while the server wakes up.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Overview

A backend API that demonstrates **production-grade engineering practices**:

- **Clean Architecture** — Repository pattern with clear separation of concerns
- **Async Operations** — Non-blocking database queries with SQLAlchemy 2.0
- **JWT Authentication** — Secure register/login flow with bcrypt password hashing
- **Multi-Tenancy** — Row-level data isolation; users only access their own tasks
- **Analytics Endpoint** — Aggregated metrics with SQL `func` and time-series filtering
- **Data Seeding** — Generate 10,000+ realistic tasks with Faker + Pandas
- **Auto-generated Docs** — Interactive Swagger UI
- **Data Validation** — Pydantic v2 schemas for every request/response

This project is part of a portfolio demonstrating **Back-End Engineering + Data Science** skills.

---

## 🏗️ Architecture

```
┌──────────────────┐
│ Client / Swagger │
└────────┬─────────┘
         │ HTTP Request + JWT
         ▼
┌──────────────────┐         ┌──────────────────┐
│  FastAPI Router  │◄───────►│ Pydantic Schemas │
└────────┬─────────┘         └──────────────────┘
         │
         ▼
┌──────────────────┐         ┌──────────────────┐
│  Auth Dependency │────────►│ JWT Verification │
│ (get_current_user)│         └──────────────────┘
└────────┬─────────┘
         │ (passes User)
         ▼
┌──────────────────┐
│ Repository Layer │◄────── Filtered by user_id
└────────┬─────────┘
         │
         ▼
┌──────────────────┐         ┌──────────────────┐
│ Database (SQLite)│◄───────►│ Faker + Pandas   │
│  users / tasks   │         │   Seed Script    │
└──────────────────┘         └──────────────────┘
```

### Project Structure

```
task-management-api/
├── app/
│   ├── api/
│   │   ├── deps.py              # get_current_user dependency
│   │   └── v1/endpoints/
│   │       ├── auth.py          # register, login, me
│   │       └── tasks.py         # CRUD + analytics
│   ├── core/
│   │   ├── config.py            # Environment settings
│   │   ├── database.py          # DB connection & session
│   │   └── security.py          # Password hashing + JWT
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── tasks.py
│   │   └── users.py
│   ├── repositories/            # Data access layer
│   │   ├── tasks_repository.py
│   │   └── users_repository.py
│   ├── schemas/                 # Pydantic validation
│   │   ├── tasks.py
│   │   └── users.py
│   └── main.py
├── scripts/
│   └── seed_data.py             # Generate 10k+ fake tasks
├── tests/                       # Pytest suite (coming soon)
├── pyproject.toml
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Hloni123252/task-management-api.git
cd task-management-api

# 2. Install dependencies
poetry install

# 3. Set up environment variables
cp .env.example .env

# 4. Run the server
poetry run python -m uvicorn app.main:app --reload
```

### Access the API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

### Live API (Deployed on Render)

- **Swagger UI:** https://task-management-api-m5rq.onrender.com/docs
- **Health Check:** https://task-management-api-m5rq.onrender.com/health

---

## 🔐 Authentication Flow

1. **Register** a user via `POST /auth/register`
2. **Login** via `POST /auth/login` → receive a JWT token
3. **Include the token** in every request:
   ```
   Authorization: Bearer <your_token>
   ```
4. **Access protected endpoints** — the server identifies you from the token

---

## 📚 API Endpoints

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Create a new user account |
| `POST` | `/auth/login` | Login and receive a JWT token |
| `GET` | `/auth/me` | Get the current logged-in user |

### Tasks (all require authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tasks/` | Create a new task (owned by current user) |
| `GET` | `/tasks/` | List current user's tasks (paginated) |
| `GET` | `/tasks/stats` | Aggregated statistics for current user |
| `GET` | `/tasks/{task_id}` | Get one of your tasks |
| `PUT` | `/tasks/{task_id}` | Update your task |
| `DELETE` | `/tasks/{task_id}` | Delete your task |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint |
| `GET` | `/health` | Health check |

---

## 📊 Analytics Response Example

```json
GET /tasks/stats
{
  "total_tasks": 10000,
  "completed_tasks": 6545,
  "pending_tasks": 3455,
  "completion_rate": 65.45,
  "tasks_created_today": 108,
  "tasks_created_this_week": 883,
  "tasks_created_this_month": 3359
}
```

Numbers are **scoped to the authenticated user** — this is a multi-tenant system.

---

## 🧪 Seeding Sample Data

Populate the database with realistic fake data using **Faker** and **Pandas**:

```bash
# 1. Register a user first (via Swagger or curl)
# 2. Then seed 10,000 tasks for that user:
poetry run python -m scripts.seed_data 10000 --email you@example.com
```

**Example output:**
```
👤 Seeding tasks for user: you@example.com (id=1)

📊 Data Analysis (using Pandas):
   Total tasks:    10000
   Completed:      6545 (65.5%)
   Pending:        3455
   Date range:     2026-06-16 -> 2026-09-14
   Busiest week:   Week 37 with 912 tasks

✅ Successfully inserted 10000 tasks for you@example.com!
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | FastAPI | High-performance async API |
| ORM | SQLAlchemy 2.0 | Async database operations |
| Validation | Pydantic v2 | Request/response schemas |
| Auth | python-jose + passlib | JWT + bcrypt password hashing |
| Database | SQLite (dev) / PostgreSQL (prod-ready) | Data persistence |
| Dependency Mgmt | Poetry | Reproducible environments |
| Server | Uvicorn | ASGI server |
| Data Generation | Faker | Realistic fake data |
| Data Analysis | Pandas | Pre-insertion analysis |

---

## 🗺️ Roadmap

- [x] Task CRUD operations
- [x] Async database operations
- [x] Auto-generated API documentation
- [x] Analytics endpoint (completion rates, trends)
- [x] Data seeding script (10k+ records)
- [x] JWT Authentication (register, login, protected routes)
- [x] Multi-tenancy (row-level isolation per user)
- [ ] Unit & integration tests (Pytest)
- [ ] PostgreSQL with Docker
- [x] Cloud deployment (Render + PostgreSQL)
- [ ] CI/CD with GitHub Actions

---

## 👤 Author

**Lehlohonolo Mtshizana**
- ALX Back-End Engineering & Data Science
- GitHub: [@Hloni123252](https://github.com/Hloni123252)

---

## 📄 License

This project is licensed under the MIT License.