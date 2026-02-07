<!-- Phase UUID: 10b7dfed-88af-432a-af4a-ca518bc3d599 -->

# README.md
```markdown
# Todo List CLI Application

A lightweight, cross‑platform command‑line tool for managing a personal to‑do list.
All data is persisted in a JSON file (`tasks.json`) so your tasks survive across sessions.

> **Why this tool?**  
> • No external dependencies – just Python 3.8+  
> • Atomic writes for data safety  
> • Simple, intuitive commands  
> • Extensible – add due dates, priorities, etc. in the future

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

The application is a single Python script.  
No installation is required beyond having Python 3.8+ installed.

```bash
# Clone the repository
git clone https://github.com/yourname/todo-cli.git
cd todo-cli

# Make the script executable (optional)
chmod +x todo_cli.py

# Run the application
./todo_cli.py
# or
python3 todo_cli.py
```

> **Tip:** If you want to run it from anywhere, add the directory to your `PATH` or create a symlink:
> ```bash
> ln -s $(pwd)/todo_cli.py /usr/local/bin/todo
> ```

---

## Usage

The CLI accepts the following commands:

| Command | Description | Example |
|---------|-------------|---------|
| `add <description>` | Add a new task | `add Buy milk` |
| `remove <id>` | Remove a task | `remove 3` |
| `complete <id>` | Mark a task as complete | `complete 2` |
| `list [--all | --completed | --incomplete]` | List tasks | `list --completed` |
| `help` | Show help | `help` |
| `exit` or `quit` | Exit the program | `exit` |

### Interactive Session

```bash
$ ./todo_cli.py
Todo List CLI Application
==========================

> add Buy groceries
Task added: 1 Buy groceries

> add Read a book
Task added: 2 Read a book

> list
○ [1] Buy groceries
○ [2] Read a book

> complete 1
Task completed: 1 Buy groceries

> list --completed
✓ [1] Buy groceries

> remove 2
Task removed: 2 Read a book

> list
✓ [1] Buy groceries

> exit
Goodbye!
```

---

## API Reference

The core of the application is the `TodoList` class.  
It can be imported and used programmatically.

```python
from todo_cli import TodoList

# Create or load existing list
todo = TodoList()          # defaults to tasks.json in current dir

# Add a task
task_id = todo.add_task("Write unit tests")

# Mark as complete
todo.complete_task(task_id)

# Remove a task
todo.remove_task(task_id)

# List tasks
all_tasks = todo.list_tasks()          # all
completed = todo.list_tasks('completed')
incomplete = todo.list_tasks('incomplete')
```

### Class: `TodoList`

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__(filename: str = "tasks.json")` | `filename` – path to JSON file | – | Loads tasks from file or creates an empty list. |
| `add_task(description: str) -> int` | `description` – task text | `int` – new task ID | Adds a task, persists, returns ID. |
| `remove_task(task_id: int) -> bool` | `task_id` – ID to remove | `True` if removed, `False` if not found | Removes task, persists. |
| `complete_task(task_id: int) -> bool` | `task_id` – ID to complete | `True` if marked, `False` if not found | Marks task as completed, persists. |
| `list_tasks(filter_status: Optional[str] = None) -> List[Dict]` | `filter_status` – `'completed'`, `'incomplete'`, or `None` | List of task dicts | Returns tasks filtered by status. |
| `get_task(task_id: int) -> Optional[Dict]` | `task_id` – ID to fetch | Task dict or `None` | Retrieves a single task. |

### Private Helpers

| Method | Description |
|--------|-------------|
| `_load_tasks()` | Reads `tasks.json` into `self.tasks`. |
| `_save_tasks()` | Writes `self.tasks` atomically to `tasks.json`. |
| `_get_next_id()` | Computes next incremental ID. |

---

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `tasks.json` | Same directory as `todo_cli.py` | Stores all tasks. |
| File permissions | Owner read/write only | Ensures data privacy. |
| Python version | 3.8+ | Required for type hints and `os.replace`. |

> **Changing the data file location**  
> Pass a custom filename when creating `TodoList`:
> ```python
> todo = TodoList(filename="~/my_tasks.json")
> ```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `Error: Task description cannot be empty.` | No description provided. | Provide a non‑empty string after `add`. |
| `Error: Task ID <id> does not exist.` | ID is wrong or task was removed. | Verify ID with `list`. |
| `Error: Unknown command.` | Typo or unsupported command. | Use `help` to see valid commands. |
| `Failed to load tasks from tasks.json` | Corrupted JSON or permission issue. | Delete or repair `tasks.json`. |
| `Failed to save tasks to tasks.json` | No write permission. | Ensure you own the file/directory. |
| `KeyboardInterrupt` or `EOFError` | Ctrl‑C or Ctrl‑D pressed. | The program exits gracefully. |
| Performance > 200 ms | Very large task list or slow disk. | Reduce number of tasks or use SSD. |

---

## Contributing

1. Fork the repo.  
2. Create a feature branch (`git checkout -b feature/foo`).  
3. Commit your changes.  
4. Run tests (`python -m unittest`).  
5. Open a pull request.

---

## License

MIT © Your Name
```

# architecture.md
```markdown
# Code Architecture

The application is intentionally simple, yet modular and testable.  
Below is a high‑level view of the main components and their responsibilities.

```
todo_cli.py
├── TodoList (class)
│   ├── __init__(filename)
│   ├── _load_tasks()
│   ├── _save_tasks()
│   ├── _get_next_id()
│   ├── add_task(description)
│   ├── remove_task(task_id)
│   ├── complete_task(task_id)
│   ├── list_tasks(filter_status)
│   └── get_task(task_id)
├── print_help()          # CLI help text
├── parse_command(args)   # Split user input into command + args
└── main()                # REPL loop
```

## Module Breakdown

| File | Purpose | Key Functions |
|------|---------|---------------|
| `todo_cli.py` | Entry point & CLI logic | `main()`, `print_help()`, `parse_command()` |
| `TodoList` | Business logic & persistence | CRUD operations, filtering, atomic writes |
| `tasks.json` | Data store | JSON array of task objects |

## Persistence Strategy

- **Atomic Write**:  
  - Write to a temporary file (`tasks.json.tmp`).  
  - Use `os.replace()` to atomically rename it to `tasks.json`.  
  - Guarantees that a crash during write leaves the original file intact.

- **Load**:  
  - On startup, read `tasks.json` if it exists.  
  - If the file is missing, start with an empty list.  
  - If the file is malformed, raise a clear error.

## Extensibility

- **Adding Fields**:  
  - Update the `task` dict in `add_task()` and adjust `list_tasks()` accordingly.  
  - No changes needed in persistence logic.

- **New Commands**:  
  - Add a new `elif` branch in `main()` and implement the logic.  
  - Keep the command parsing simple (no external libs).

- **Unit Tests**:  
  - The `TodoList` class is pure Python and can be unit‑tested in isolation.  
  - Tests should cover CRUD operations, edge cases, and error handling.

## Design Principles

- **Single Responsibility**:  
  - `TodoList` handles data; `main()` handles user interaction.

- **Atomicity**:  
  - All writes are atomic to prevent data corruption.

- **Minimal Dependencies**:  
  - Only the Python standard library is used.

- **PEP 8 & Type Hints**:  
  - Code follows PEP 8 and includes type hints for clarity.

---

# usage.md
```markdown
# Usage Examples

Below are common scenarios you might encounter while using the Todo List CLI.

## 1. Adding Tasks

```bash
> add Buy milk
Task added: 1 Buy milk
```

> **Tip:** If your description contains spaces, you can wrap it in quotes:
> ```bash
> > add "Finish the report by Friday"
> Task added: 2 Finish the report by Friday
> ```

## 2. Listing Tasks

```bash
> list
○ [1] Buy milk
○ [2] Finish the report by Friday
```

### Filter by Status

```bash
> list --completed
✓ [1] Buy milk

> list --incomplete
○ [2] Finish the report by Friday
```

## 3. Completing a Task

```bash
> complete 1
Task completed: 1 Buy milk
```

## 4. Removing a Task

```bash
> remove 2
Task removed: 2 Finish the report by Friday
```

## 5. Help

```bash
> help
Todo List CLI Application

Available commands:
  add <task description>     Add a new task
  remove <task id>           Remove a task by ID
  complete <task id>         Mark a task as complete
  list [--all | --completed | --incomplete]  List tasks
  help                       Show this help message
  exit or quit               Exit the application

Examples:
  add "Buy groceries"
  remove 1
  complete 2
  list
  list --completed
  list --incomplete
```

## 6. Exiting

```bash
> exit
Goodbye!
```

---

# config.md
```markdown
# Configuration Guide

The Todo List CLI is intentionally minimal, but you can tweak a few settings.

## 1. Data File Location

By default, the application reads/writes `tasks.json` in the same directory as `todo_cli.py`.  
To change this, instantiate `TodoList` with a custom path:

```python
from todo_cli import TodoList

# Store tasks in a hidden file in the user's home directory
todo = TodoList(filename="~/.todo/tasks.json")
```

> **Note:** The `~` will be expanded by `pathlib` automatically.

## 2. File Permissions

On Unix‑like systems, the script sets the file to **owner read/write only**.  
If you need to adjust permissions manually:

```bash
chmod 600 tasks.json
```

## 3. Python Version

The script requires **Python 3.8+**.  
Check your version:

```bash
python3 --version
# Should output: Python 3.8.x or newer
```

## 4. Running as a Service

If you want the CLI to run in the background (e.g., as a daemon), you can wrap it in a shell script or use a process manager like `systemd` or `supervisord`.  
The script is fully interactive, so background execution is only useful for automation scripts that pipe commands into it.

---

# troubleshooting.md
```markdown
# Troubleshooting

Below are common issues and how to resolve them.

## 1. `Error: Task description cannot be empty.`

- **Cause**: The `add` command was invoked without a description.
- **Fix**: Provide a non‑empty description.
  ```bash
  > add Read the documentation
  ```

## 2. `Error: Task ID <id> does not exist.`

- **Cause**: The specified ID is not present in the current list.
- **Fix**: Verify the ID with `list` and use the correct number.

## 3. `Error: Unknown command.`

- **Cause**: Typo or unsupported command.
- **Fix**: Run `help` to see the list of valid commands.

## 4. `Failed to load tasks from tasks.json`

- **Cause**: The JSON file is corrupted or unreadable.
- **Fix**:
  1. Delete or rename the corrupted file.
  2. Restart the application; a fresh `tasks.json` will be created.

## 5. `Failed to save tasks to tasks.json`

- **Cause**: Insufficient write permissions or disk full.
- **Fix**:
  - Ensure you own the directory and have write permission.
  - Free up disk space if necessary.

## 6. `KeyboardInterrupt` or `EOFError`

- **Cause**: User pressed `Ctrl‑C` or `Ctrl‑D`.
- **Fix**: The program exits gracefully. No action needed.

## 7. Performance Issues (>200 ms)

- **Cause**: Very large task list or slow storage medium.
- **Fix**:
  - Reduce the number of tasks.
  - Use a faster storage device (SSD).

## 8. Unexpected Exceptions

- **Cause**: Rare bugs or environment issues.
- **Fix**:
  1. Run the script with `-v` or `--debug` if added.
  2. Check the stack trace for the exact line.
  3. Report the issue on the project's issue tracker.

---

# Contributing

We welcome contributions! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

# License

MIT © Your Name
```

---