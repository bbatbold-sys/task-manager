"""Tests for the Task dataclass."""

import pytest
from src.models import Task


def test_task_defaults():
    t = Task(id=1, title="Test task")
    assert t.id == 1
    assert t.title == "Test task"
    assert t.description == ""
    assert t.priority == "medium"
    assert t.status == "todo"
    assert t.due_date is None


def test_task_to_dict():
    t = Task(id=2, title="Buy milk", priority="high", due_date="2026-04-01")
    d = t.to_dict()
    assert d["id"] == 2
    assert d["title"] == "Buy milk"
    assert d["priority"] == "high"
    assert d["due_date"] == "2026-04-01"
    assert d["status"] == "todo"


def test_task_from_dict():
    data = {
        "id": 3,
        "title": "Read book",
        "description": "Finish chapter 5",
        "due_date": "2026-03-20",
        "priority": "low",
        "status": "done",
        "created_at": "2026-03-01T09:00:00",
        "updated_at": "2026-03-10T12:00:00",
    }
    t = Task.from_dict(data)
    assert t.id == 3
    assert t.title == "Read book"
    assert t.description == "Finish chapter 5"
    assert t.status == "done"
    assert t.priority == "low"


def test_task_roundtrip():
    original = Task(id=5, title="Roundtrip", description="Check serialization", priority="high")
    restored = Task.from_dict(original.to_dict())
    assert restored.id == original.id
    assert restored.title == original.title
    assert restored.description == original.description
    assert restored.priority == original.priority
    assert restored.status == original.status
