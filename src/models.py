"""Task dataclass and related types."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional


Priority = Literal["high", "medium", "low"]
Status = Literal["todo", "done"]


@dataclass
class Task:
    """Represents a single task."""

    id: int
    title: str
    description: str = ""
    due_date: Optional[str] = None
    priority: Priority = "medium"
    status: Status = "todo"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict:
        """Serialize task to a plain dict."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Deserialize a task from a plain dict."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            priority=data.get("priority", "medium"),
            status=data.get("status", "todo"),
            created_at=data.get("created_at", datetime.now().isoformat(timespec="seconds")),
            updated_at=data.get("updated_at", datetime.now().isoformat(timespec="seconds")),
        )
