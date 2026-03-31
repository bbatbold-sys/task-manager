# Task Manager

A feature-rich task management web app built with Python and Streamlit.

## Features

- **Add tasks** – title, description, due date, priority, project, tags, subtasks, recurring schedule
- **List tasks** – two-column board (In Progress / Completed)
- **Complete tasks** – one-click done, with undo support
- **Delete & archive tasks** – remove or archive individually or in bulk
- **Calendar view** – monthly calendar showing tasks by due date
- **Search & filter** – by keyword, priority, project, tag, or due today
- **Sort** – by priority, due date, created date, title, or manual order
- **Time tracking** – start/stop timer per task with total tracked time
- **Pomodoro timer** – built-in 25/5 work-break timer in the sidebar
- **Subtasks** – checklist inside each task with progress bar
- **Notes** – attach notes to any task
- **Recurring tasks** – daily, weekly, or monthly auto-scheduling
- **Export CSV** – download all tasks as a spreadsheet

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Data models | Python dataclasses (`src/models.py`) |
| Storage | JSON file via `src/storage.py` |
| CLI | Click (`src/cli.py`) |
| Tests | pytest |

## Project Structure

```
task-manager/
├── app.py            # Streamlit web UI (main entry point)
├── src/
│   ├── models.py     # Task, Subtask, TaskNote, TimeEntry dataclasses
│   ├── storage.py    # load/save/update/delete tasks (JSON persistence)
│   └── cli.py        # Command-line interface (Click)
├── tests/
│   ├── test_models.py
│   ├── test_storage.py
│   └── test_cli.py
├── tasks.json        # Persistent task data
└── pyproject.toml
```

## Setup

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/bbatbold-sys/task-manager.git
cd task-manager

# Install dependencies
pip install streamlit
pip install -e .
```

### Run the web app

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

### Run the CLI

```bash
# Add a task
task add "Buy groceries" --priority high --due 2026-04-01

# List all tasks
task list

# Mark a task done
task done 1

# Delete a task
task delete 1
```

## Usage Examples

### Adding a task with details

Fill in the **＋ New Task** panel in the sidebar:
- **Title** – required
- **Due date** – pick from calendar
- **Priority** – high / medium / low
- **Project** – group tasks by project name
- **Tags** – pick existing or add new comma-separated tags
- **Subtasks** – one per line, become a checklist inside the card
- **Repeat** – set daily / weekly / monthly to auto-create the next occurrence when completed

### Calendar view

Click the **📅 Calendar** tab to see all tasks with due dates placed on a monthly grid. Navigate months with ← Prev / Next →.

### Filtering tasks

Open **🔍 Search & Filters** in the sidebar to filter by keyword, priority, project, tag, or show only today's tasks.

### Exporting

Click **⬇ Export CSV** at the bottom of the Tasks tab to download all tasks as a CSV file.

## Running Tests

```bash
pytest
```

## Dependencies

- `streamlit` – web UI framework
- `click` – CLI framework
- `pytest` – test runner

## License

MIT
