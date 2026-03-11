"""CLI entry point for the Task Manager."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from .models import Task
from .storage import delete_task, get_task, load_tasks, next_id, save_tasks, update_task

STORAGE_PATH = Path("tasks.json")

PRIORITY_COLORS = {"high": "red", "medium": "yellow", "low": "green"}
STATUS_COLORS = {"done": "green", "todo": "white"}


@click.group()
def cli() -> None:
    """Personal task manager."""


@cli.command("add")
@click.argument("title")
@click.option("--description", "-d", default="", help="Task description.")
@click.option("--due", default=None, help="Due date (YYYY-MM-DD).")
@click.option(
    "--priority",
    "-p",
    type=click.Choice(["high", "medium", "low"]),
    default="medium",
    help="Task priority.",
)
def add_task(title: str, description: str, due: Optional[str], priority: str) -> None:
    """Add a new task."""
    if due:
        try:
            datetime.strptime(due, "%Y-%m-%d")
        except ValueError:
            raise click.BadParameter("Due date must be in YYYY-MM-DD format.", param_hint="'--due'")

    task_id = next_id(STORAGE_PATH)
    task = Task(id=task_id, title=title, description=description, due_date=due, priority=priority)
    tasks = load_tasks(STORAGE_PATH)
    tasks.append(task)
    save_tasks(tasks, STORAGE_PATH)
    click.echo(f"Added task #{task_id}: {title}")


@cli.command("list")
@click.option(
    "--status",
    type=click.Choice(["todo", "done"]),
    default=None,
    help="Filter by status.",
)
@click.option(
    "--priority",
    type=click.Choice(["high", "medium", "low"]),
    default=None,
    help="Filter by priority.",
)
def list_tasks(status: Optional[str], priority: Optional[str]) -> None:
    """List tasks."""
    tasks = load_tasks(STORAGE_PATH)

    if status:
        tasks = [t for t in tasks if t.status == status]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]

    if not tasks:
        click.echo("No tasks found.")
        return

    for t in tasks:
        due_str = f"  due {t.due_date}" if t.due_date else ""
        priority_label = click.style(f"[{t.priority}]", fg=PRIORITY_COLORS.get(t.priority, "white"))
        status_label = click.style(f"[{t.status}]", fg=STATUS_COLORS.get(t.status, "white"))
        click.echo(f"  #{t.id}  {status_label} {priority_label}  {t.title}{due_str}")
        if t.description:
            click.echo(f"       {t.description}")


@cli.command("done")
@click.argument("task_id", type=int)
def mark_done(task_id: int) -> None:
    """Mark a task as done."""
    task = get_task(task_id, STORAGE_PATH)
    if task is None:
        raise click.ClickException(f"Task #{task_id} not found.")
    task.status = "done"
    task.updated_at = datetime.now().isoformat(timespec="seconds")
    update_task(task, STORAGE_PATH)
    click.echo(f"Task #{task_id} marked as done.")


@cli.command("delete")
@click.argument("task_id", type=int)
def remove_task(task_id: int) -> None:
    """Delete a task."""
    if not delete_task(task_id, STORAGE_PATH):
        raise click.ClickException(f"Task #{task_id} not found.")
    click.echo(f"Task #{task_id} deleted.")


@cli.command("edit")
@click.argument("task_id", type=int)
@click.option("--title", default=None, help="New title.")
@click.option("--description", "-d", default=None, help="New description.")
@click.option("--due", default=None, help="New due date (YYYY-MM-DD).")
@click.option(
    "--priority",
    type=click.Choice(["high", "medium", "low"]),
    default=None,
    help="New priority.",
)
def edit_task(
    task_id: int,
    title: Optional[str],
    description: Optional[str],
    due: Optional[str],
    priority: Optional[str],
) -> None:
    """Edit a task."""
    task = get_task(task_id, STORAGE_PATH)
    if task is None:
        raise click.ClickException(f"Task #{task_id} not found.")

    if due:
        try:
            datetime.strptime(due, "%Y-%m-%d")
        except ValueError:
            raise click.BadParameter("Due date must be in YYYY-MM-DD format.", param_hint="'--due'")

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if due is not None:
        task.due_date = due
    if priority is not None:
        task.priority = priority  # type: ignore[assignment]

    task.updated_at = datetime.now().isoformat(timespec="seconds")
    update_task(task, STORAGE_PATH)
    click.echo(f"Task #{task_id} updated.")


@cli.command("search")
@click.argument("keyword")
def search_tasks(keyword: str) -> None:
    """Search tasks by keyword."""
    tasks = load_tasks(STORAGE_PATH)
    kw = keyword.lower()
    matches = [t for t in tasks if kw in t.title.lower() or kw in t.description.lower()]

    if not matches:
        click.echo(f"No tasks matching '{keyword}'.")
        return

    for t in matches:
        due_str = f"  due {t.due_date}" if t.due_date else ""
        click.echo(f"  #{t.id}  [{t.status}] [{t.priority}]  {t.title}{due_str}")
        if t.description:
            click.echo(f"       {t.description}")
