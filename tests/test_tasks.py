"""
Tests for the task endpoints.

Covers:
- Task CRUD (create, read, update, delete)
- Multi-tenancy: users cannot access each other's tasks
- Analytics: per-user statistics
- Pagination: skip/limit behavior
"""


# ============================================================
# Category 1: Task CRUD (basic functionality)
# ============================================================

async def test_create_task_success(auth_client):
    """An authenticated user can create a task."""
    response = await auth_client.post(
        "/tasks/",
        json={
            "title": "My first task",
            "description": "Test description",
            "completed": False,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My first task"
    assert data["description"] == "Test description"
    assert data["completed"] is False
    assert "id" in data
    assert "user_id" in data  # Response includes owner


async def test_create_task_unauthenticated(client):
    """Creating a task without a token returns 401."""
    response = await client.post(
        "/tasks/",
        json={"title": "Anonymous task", "completed": False},
    )
    assert response.status_code == 401


async def test_get_all_tasks(auth_client):
    """User sees only their own tasks (should return a list)."""
    # Create two tasks
    await auth_client.post(
        "/tasks/", json={"title": "Task A", "completed": False}
    )
    await auth_client.post(
        "/tasks/", json={"title": "Task B", "completed": True}
    )

    # Fetch all
    response = await auth_client.get("/tasks/")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    titles = {t["title"] for t in tasks}
    assert titles == {"Task A", "Task B"}


async def test_get_task_by_id(auth_client):
    """User can fetch one of their own tasks by ID."""
    # Create
    create_response = await auth_client.post(
        "/tasks/", json={"title": "Specific task", "completed": False}
    )
    task_id = create_response.json()["id"]

    # Fetch
    response = await auth_client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "Specific task"


async def test_get_task_not_found(auth_client):
    """Fetching a task that doesn't exist returns 404."""
    response = await auth_client.get("/tasks/99999")
    assert response.status_code == 404


async def test_update_task(auth_client):
    """User can update their own task."""
    # Create
    create_response = await auth_client.post(
        "/tasks/",
        json={"title": "Old title", "completed": False},
    )
    task_id = create_response.json()["id"]

    # Update
    response = await auth_client.put(
        f"/tasks/{task_id}",
        json={"title": "New title", "completed": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["completed"] is True


async def test_delete_task(auth_client):
    """User can delete their own task."""
    # Create
    create_response = await auth_client.post(
        "/tasks/", json={"title": "To be deleted", "completed": False}
    )
    task_id = create_response.json()["id"]

    # Delete
    response = await auth_client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify gone
    verify = await auth_client.get(f"/tasks/{task_id}")
    assert verify.status_code == 404


# ============================================================
# Category 2: Multi-Tenancy (the security tests)
# ============================================================

async def test_user_cannot_see_other_users_tasks(auth_client, second_auth_client):
    """
    User A creates tasks. User B's GET /tasks returns an empty list.
    
    This proves data isolation at the LIST level.
    """
    # User A creates a task
    await auth_client.post(
        "/tasks/", json={"title": "User A's secret", "completed": False}
    )

    # User B fetches their list
    response = await second_auth_client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []  # Empty — User B sees nothing


async def test_user_cannot_get_other_users_task_by_id(
    auth_client, second_auth_client
):
    """
    User A creates a task with ID X. User B requests /tasks/X.
    Should return 404 — the task "does not exist" from User B's view.
    """
    # User A creates
    create_response = await auth_client.post(
        "/tasks/", json={"title": "User A's task", "completed": False}
    )
    task_id = create_response.json()["id"]

    # User B tries to fetch it
    response = await second_auth_client.get(f"/tasks/{task_id}")
    assert response.status_code == 404  # Not 403 — "doesn't exist" for them


async def test_user_cannot_update_other_users_task(
    auth_client, second_auth_client
):
    """User B cannot modify User A's task."""
    # User A creates
    create_response = await auth_client.post(
        "/tasks/", json={"title": "Original", "completed": False}
    )
    task_id = create_response.json()["id"]

    # User B tries to update
    response = await second_auth_client.put(
        f"/tasks/{task_id}",
        json={"title": "Hijacked!", "completed": True},
    )
    assert response.status_code == 404

    # Verify the task is unchanged (from User A's view)
    verify = await auth_client.get(f"/tasks/{task_id}")
    assert verify.json()["title"] == "Original"


async def test_user_cannot_delete_other_users_task(
    auth_client, second_auth_client
):
    """User B cannot delete User A's task."""
    # User A creates
    create_response = await auth_client.post(
        "/tasks/", json={"title": "Safe task", "completed": False}
    )
    task_id = create_response.json()["id"]

    # User B tries to delete
    response = await second_auth_client.delete(f"/tasks/{task_id}")
    assert response.status_code == 404

    # Verify the task still exists (from User A's view)
    verify = await auth_client.get(f"/tasks/{task_id}")
    assert verify.status_code == 200
    assert verify.json()["title"] == "Safe task"


# ============================================================
# Category 3: Analytics
# ============================================================

async def test_stats_empty_user(second_auth_client):
    """A brand-new user with no tasks has all-zero stats."""
    response = await second_auth_client.get("/tasks/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 0
    assert data["completed_tasks"] == 0
    assert data["pending_tasks"] == 0
    assert data["completion_rate"] == 0.0


async def test_stats_with_tasks(auth_client):
    """Stats reflect the user's actual tasks."""
    # Create 3 tasks: 2 completed, 1 pending
    await auth_client.post("/tasks/", json={"title": "T1", "completed": True})
    await auth_client.post("/tasks/", json={"title": "T2", "completed": True})
    await auth_client.post("/tasks/", json={"title": "T3", "completed": False})

    response = await auth_client.get("/tasks/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 3
    assert data["completed_tasks"] == 2
    assert data["pending_tasks"] == 1
    assert data["completion_rate"] == 66.67  # 2/3 * 100


async def test_stats_isolated_per_user(auth_client, second_auth_client):
    """
    User A's stats must NOT include User B's tasks.
    
    This proves analytics respects row-level isolation.
    """
    # User A creates 2 tasks
    await auth_client.post("/tasks/", json={"title": "A1", "completed": True})
    await auth_client.post("/tasks/", json={"title": "A2", "completed": True})

    # User B creates 1 task
    await second_auth_client.post(
        "/tasks/", json={"title": "B1", "completed": False}
    )

    # User A's stats: 2 tasks
    response_a = await auth_client.get("/tasks/stats")
    assert response_a.json()["total_tasks"] == 2
    assert response_a.json()["completed_tasks"] == 2

    # User B's stats: 1 task
    response_b = await second_auth_client.get("/tasks/stats")
    assert response_b.json()["total_tasks"] == 1
    assert response_b.json()["completed_tasks"] == 0


# ============================================================
# Category 4: Pagination
# ============================================================

async def test_pagination_limit(auth_client):
    """`limit` query parameter restricts the number of results."""
    # Create 5 tasks
    for i in range(5):
        await auth_client.post(
            "/tasks/", json={"title": f"Task {i}", "completed": False}
        )

    response = await auth_client.get("/tasks/?limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_pagination_skip(auth_client):
    """`skip` query parameter skips the first N results."""
    # Create 5 tasks
    for i in range(5):
        await auth_client.post(
            "/tasks/", json={"title": f"Task {i}", "completed": False}
        )

    # Get all (should be 5)
    all_tasks = await auth_client.get("/tasks/")
    assert len(all_tasks.json()) == 5

    # Skip 3 (should get 2)
    response = await auth_client.get("/tasks/?skip=3")
    assert response.status_code == 200
    assert len(response.json()) == 2