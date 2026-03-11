"""Tests for JSON storage utilities."""

import json
import pytest
from pathlib import Path

from src.models import Task
from src.storage import (
    load_tasks,
    save_tasks,
    next_id,
    get_task,
    update_task,
    delete_task,
)


@pytest.fixture
def tmp_storage(tmp_path):
    """Return a temp path for a storage file."""
    return tmp_path / "tasks.json"


def test_load_tasks_empty(tmp_storage):
    tasks = load_tasks(tmp_storage)
    assert tasks == []


def test_save_and_load(tmp_storage):
    tasks = [Task(id=1, title="First"), Task(id=2, title="Second")]
    save_tasks(tasks, tmp_storage)
    loaded = load_tasks(tmp_storage)
    assert len(loaded) == 2
    assert loaded[0].title == "First"
    assert loaded[1].title == "Second"


def test_next_id_sequential(tmp_storage):
    id1 = next_id(tmp_storage)
    id2 = next_id(tmp_storage)
    id3 = next_id(tmp_storage)
    assert id1 == 1
    assert id2 == 2
    assert id3 == 3


def test_get_task_found(tmp_storage):
    tasks = [Task(id=1, title="Alpha"), Task(id=2, title="Beta")]
    save_tasks(tasks, tmp_storage)
    found = get_task(2, tmp_storage)
    assert found is not None
    assert found.title == "Beta"


def test_get_task_not_found(tmp_storage):
    assert get_task(99, tmp_storage) is None


def test_update_task(tmp_storage):
    tasks = [Task(id=1, title="Original")]
    save_tasks(tasks, tmp_storage)
    updated = Task(id=1, title="Updated", status="done")
    result = update_task(updated, tmp_storage)
    assert result is True
    loaded = get_task(1, tmp_storage)
    assert loaded.title == "Updated"
    assert loaded.status == "done"


def test_update_task_not_found(tmp_storage):
    result = update_task(Task(id=99, title="Ghost"), tmp_storage)
    assert result is False


def test_delete_task(tmp_storage):
    tasks = [Task(id=1, title="Keep"), Task(id=2, title="Delete me")]
    save_tasks(tasks, tmp_storage)
    result = delete_task(2, tmp_storage)
    assert result is True
    remaining = load_tasks(tmp_storage)
    assert len(remaining) == 1
    assert remaining[0].id == 1


def test_delete_task_not_found(tmp_storage):
    result = delete_task(99, tmp_storage)
    assert result is False
