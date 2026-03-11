"""JSON-based storage utilities for tasks."""

import json
from pathlib import Path
from typing import List, Optional

from .models import Task

DEFAULT_PATH = Path("tasks.json")


def _load_raw(path: Path) -> dict:
    """Load raw JSON data from file, returning empty structure if missing."""
    if not path.exists():
        return {"tasks": [], "next_id": 1}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_raw(data: dict, path: Path) -> None:
    """Write raw JSON data to file."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_tasks(path: Path = DEFAULT_PATH) -> List[Task]:
    """Load all tasks from storage."""
    data = _load_raw(path)
    return [Task.from_dict(t) for t in data.get("tasks", [])]


def save_tasks(tasks: List[Task], path: Path = DEFAULT_PATH, next_id: Optional[int] = None) -> None:
    """Persist all tasks to storage."""
    data = _load_raw(path)
    if next_id is not None:
        data["next_id"] = next_id
    data["tasks"] = [t.to_dict() for t in tasks]
    _save_raw(data, path)


def next_id(path: Path = DEFAULT_PATH) -> int:
    """Return the next available task ID and increment the counter."""
    data = _load_raw(path)
    nid = data.get("next_id", 1)
    data["next_id"] = nid + 1
    # preserve tasks list
    _save_raw(data, path)
    return nid


def get_task(task_id: int, path: Path = DEFAULT_PATH) -> Optional[Task]:
    """Retrieve a single task by ID, or None if not found."""
    for task in load_tasks(path):
        if task.id == task_id:
            return task
    return None


def update_task(updated: Task, path: Path = DEFAULT_PATH) -> bool:
    """Replace a task with the same ID. Returns True if found and updated."""
    tasks = load_tasks(path)
    for i, t in enumerate(tasks):
        if t.id == updated.id:
            tasks[i] = updated
            save_tasks(tasks, path)
            return True
    return False


def delete_task(task_id: int, path: Path = DEFAULT_PATH) -> bool:
    """Remove a task by ID. Returns True if found and deleted."""
    tasks = load_tasks(path)
    original_len = len(tasks)
    tasks = [t for t in tasks if t.id != task_id]
    if len(tasks) == original_len:
        return False
    save_tasks(tasks, path)
    return True
