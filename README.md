# Task Management API

> A production-grade REST API for task management with analytics, built with FastAPI, SQLAlchemy, and PostgreSQL/SQLite.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Overview

A backend API that demonstrates **production-grade engineering practices** including:

- **Clean Architecture** — Repository pattern, separation of concerns
- **Async Operations** — Non-blocking database queries with SQLAlchemy 2.0
- **Auto-generated Documentation** — Interactive Swagger UI
- **Data Validation** — Pydantic schemas for request/response
- **Environment Management** — Poetry for dependency management
- **Analytics Ready** — Foundation for data aggregation endpoints

This project is part of a portfolio demonstrating **Back-End Engineering + Data Science** skills.

---

## 🏗️ Architecture

```mermaid
graph TD
    A[Client / Swagger UI] -->|HTTP Request| B[FastAPI Router]
    B --> C[Service Layer - Business Logic]
    C --> D[Repository Layer - Data Access]
    D --> E[(Database - SQLite/PostgreSQL)]
    B --> F[Pydantic Schemas - Validation]
    F --> B
