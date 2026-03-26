"""Task dataclass and related types."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal, Optional


Priority = Literal["high", "medium", "low"]
Status = Literal["todo", "done"]


@dataclass
class Subtask:
    """A checklist item inside a task."""
    text: str
    done: bool = False

    def to_dict(self) -> dict:
        return {"text": self.text, "done": self.done}

    @classmethod
    def from_dict(cls, data: dict) -> "Subtask":
        return cls(text=data.get("text", ""), done=data.get("done", False))


@dataclass
class TaskNote:
    """A timestamped note/comment on a task."""
    text: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict:
        return {"text": self.text, "created_at": self.created_at}

    @classmethod
    def from_dict(cls, data: dict) -> "TaskNote":
        return cls(
            text=data.get("text", ""),
            created_at=data.get("created_at", datetime.now().isoformat(timespec="seconds")),
        )


@dataclass
class TimeEntry:
    """A start/stop time-tracking entry."""
    start: str
    end: Optional[str] = None  # None means currently running

    def to_dict(self) -> dict:
        return {"start": self.start, "end": self.end}

    @classmethod
    def from_dict(cls, data: dict) -> "TimeEntry":
        return cls(start=data.get("start", ""), end=data.get("end"))

    def duration_seconds(self) -> int:
        """Return elapsed seconds for this entry (uses now if still running)."""
        fmt = "%Y-%m-%dT%H:%M:%S"
        try:
            start_dt = datetime.fromisoformat(self.start)
        except ValueError:
            return 0
        if self.end:
            try:
                end_dt = datetime.fromisoformat(self.end)
            except ValueError:
                end_dt = datetime.now()
        else:
            end_dt = datetime.now()
        return max(0, int((end_dt - start_dt).total_seconds()))


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

    # ── New fields (all backward-compatible via .get() in from_dict) ──
    tags: List[str] = field(default_factory=list)
    subtasks: List[Subtask] = field(default_factory=list)
    notes: List[TaskNote] = field(default_factory=list)
    time_entries: List[TimeEntry] = field(default_factory=list)
    recurring: Optional[str] = None          # "daily" | "weekly" | "monthly" | None
    project: Optional[str] = None
    archived: bool = False
    order: int = 0

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
            "tags": self.tags,
            "subtasks": [s.to_dict() for s in self.subtasks],
            "notes": [n.to_dict() for n in self.notes],
            "time_entries": [e.to_dict() for e in self.time_entries],
            "recurring": self.recurring,
            "project": self.project,
            "archived": self.archived,
            "order": self.order,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Deserialize a task from a plain dict (backward-compatible)."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            priority=data.get("priority", "medium"),
            status=data.get("status", "todo"),
            created_at=data.get("created_at", datetime.now().isoformat(timespec="seconds")),
            updated_at=data.get("updated_at", datetime.now().isoformat(timespec="seconds")),
            tags=data.get("tags", []),
            subtasks=[Subtask.from_dict(s) for s in data.get("subtasks", [])],
            notes=[TaskNote.from_dict(n) for n in data.get("notes", [])],
            time_entries=[TimeEntry.from_dict(e) for e in data.get("time_entries", [])],
            recurring=data.get("recurring"),
            project=data.get("project"),
            archived=data.get("archived", False),
            order=data.get("order", 0),
        )
