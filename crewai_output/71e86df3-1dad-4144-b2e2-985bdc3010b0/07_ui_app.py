# Phase UUID: 71428240-de57-4c5e-b92d-db44e0560d6f

#!/usr/bin/env python3
"""
Streamlit UI for the Todo List CLI Application
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st


# --------------------------------------------------------------------------- #
#  Persistence layer – same logic as the CLI version
# --------------------------------------------------------------------------- #
class TodoList:
    """
    Manage a todo list with persistence to a JSON file.
    """

    def __init__(self, filename: str = "tasks.json"):
        self.filename = Path(filename)
        self.tasks: List[Dict[str, Any]] = []
        self._load_tasks()

    def _load_tasks(self) -> None:
        """Load tasks from the JSON file."""
        if self.filename.exists():
            try:
                with self.filename.open("r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                st.exception(f"Failed to load tasks: {exc}")
                self.tasks = []
        else:
            self.tasks = []

    def _save_tasks(self) -> None:
        """Save tasks to the JSON file using an atomic write."""
        temp_file = self.filename.with_suffix(".tmp")
        try:
            with temp_file.open("w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=2)
            temp_file.replace(self.filename)
        except OSError as exc:
            st.exception(f"Failed to save tasks: {exc}")

    def _get_next_id(self) -> int:
        """Return the next available task ID."""
        return max((t["id"] for t in self.tasks), default=0) + 1

    def add_task(self, description: str) -> int:
        """Add a new task and persist the change."""
        if not description.strip():
            raise ValueError("Task description cannot be empty.")
        task_id = self._get_next_id()
        self.tasks.append(
            {"id": task_id, "description": description.strip(), "completed": False}
        )
        self._save_tasks()
        return task_id

    def remove_task(self, task_id: int) -> bool:
        """Remove a task by ID."""
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                del self.tasks[i]
                self._save_tasks()
                return True
        return False

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed."""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                self._save_tasks()
                return True
        return False

    def list_tasks(self, filter_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return tasks filtered by status."""
        if filter_status == "completed":
            return [t for t in self.tasks if t["completed"]]
        if filter_status == "incomplete":
            return [t for t in self.tasks if not t["completed"]]
        return self.tasks

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a task by ID."""
        return next((t for t in self.tasks if t["id"] == task_id), None)


# --------------------------------------------------------------------------- #
#  Streamlit UI
# --------------------------------------------------------------------------- #
def get_todo_list() -> TodoList:
    """Return the TodoList instance stored in session_state."""
    if "todo_list" not in st.session_state:
        st.session_state.todo_list = TodoList()
    return st.session_state.todo_list


def main() -> None:
    # Page configuration
    st.set_page_config(
        page_title="Todo List",
        page_icon="🗒️",
        layout="wide",
    )

    # Load tasks once – show a spinner while loading
    with st.spinner("Loading tasks…"):
        todo = get_todo_list()

    # --------------------------------------------------------------------- #
    #  Sidebar navigation
    # --------------------------------------------------------------------- #
    st.sidebar.title("Navigation")
    view = st.sidebar.radio(
        "Select view",
        options=[
            "Add Task",
            "Remove Task",
            "Complete Task",
            "List Tasks",
            "Help",
        ],
    )

    # --------------------------------------------------------------------- #
    #  Main tabs – we still use tabs for layout, but the sidebar controls
    #  which tab is shown.  The other tabs are hidden to avoid confusion.
    # --------------------------------------------------------------------- #
    tab_names = ["Add Task", "Remove Task", "Complete Task", "List Tasks", "Help"]
    tabs = st.tabs(tab_names)

    # Helper to hide all tabs except the selected one
    def hide_other_tabs(selected: str) -> None:
        for name, tab in zip(tab_names, tabs):
            if name != selected:
                with tab:
                    st.empty()  # clear content

    hide_other_tabs(view)

    # --------------------------------------------------------------------- #
    #  Add Task tab
    # --------------------------------------------------------------------- #
    with tabs[0]:
        st.header("Add a New Task")
        col1, col2 = st.columns([3, 1])
        with col1:
            task_desc = st.text_input(
                "Task description",
                key="add_desc",
                placeholder="Enter task description here",
            )
        with col2:
            if st.button("Add Task", key="add_btn"):
                try:
                    with st.spinner("Adding task…"):
                        task_id = todo.add_task(task_desc)
                    st.success(f"✅ Task added: [{task_id}] {task_desc.strip()}")
                    # Reset input field
                    st.session_state.add_desc = ""
                except ValueError as exc:
                    st.error(f"❌ {exc}")
                except Exception as exc:
                    st.exception(f"Unexpected error: {exc}")

    # --------------------------------------------------------------------- #
    #  Remove Task tab
    # --------------------------------------------------------------------- #
    with tabs[1]:
        st.header("Remove an Existing Task")
        if not todo.tasks:
            st.warning("No tasks to remove.")
        else:
            task_options = [
                f"[{t['id']}] {t['description']}" for t in todo.tasks
            ]
            selected = st.selectbox(
                "Select task to remove",
                options=task_options,
                key="remove_select",
            )
            if st.button("Remove Task", key="remove_btn"):
                try:
                    task_id = int(selected.split()[1][:-1])  # extract ID
                    with st.spinner("Removing task…"):
                        removed = todo.remove_task(task_id)
                    if removed:
                        st.success(f"✅ Task removed: {selected}")
                    else:
                        st.error("❌ Task not found.")
                except Exception as exc:
                    st.exception(f"Unexpected error: {exc}")

    # --------------------------------------------------------------------- #
    #  Complete Task tab
    # --------------------------------------------------------------------- #
    with tabs[2]:
        st.header("Mark a Task as Completed")
        incomplete_tasks = [t for t in todo.tasks if not t["completed"]]
        if not incomplete_tasks:
            st.info("All tasks are already completed.")
        else:
            task_options = [
                f"[{t['id']}] {t['description']}" for t in incomplete_tasks
            ]
            selected = st.selectbox(
                "Select task to complete",
                options=task_options,
                key="complete_select",
            )
            if st.button("Mark as Completed", key="complete_btn"):
                try:
                    task_id = int(selected.split()[1][:-1])  # extract ID
                    with st.spinner("Marking task as completed…"):
                        completed = todo.complete_task(task_id)
                    if completed:
                        st.success(f"✅ Task completed: {selected}")
                    else:
                        st.error("❌ Task not found.")
                except Exception as exc:
                    st.exception(f"Unexpected error: {exc}")

    # --------------------------------------------------------------------- #
    #  List Tasks tab
    # --------------------------------------------------------------------- #
    with tabs[3]:
        st.header("Task List")
        filter_option = st.radio(
            "Filter tasks",
            options=["All", "Completed", "Incomplete"],
            index=0,
            key="filter_radio",
        )
        filter_map = {"All": None, "Completed": "completed", "Incomplete": "incomplete"}
        filtered = todo.list_tasks(filter_map[filter_option])

        if not filtered:
            st.info(f"No {filter_option.lower()} tasks found.")
        else:
            # Display as a table
            df = {
                "ID": [t["id"] for t in filtered],
                "Description": [t["description"] for t in filtered],
                "Status": ["✓" if t["completed"] else "○" for t in filtered],
            }
            st.table(df)

        # Show raw JSON in an expander
        with st.expander("Show raw JSON"):
            st.json(todo.tasks)

    # --------------------------------------------------------------------- #
    #  Help tab
    # --------------------------------------------------------------------- #
    with tabs[4]:
        st.header("Help & Usage")
        help_text = """
**Todo List Streamlit App**

- **Add Task**: Enter a description and click *Add Task*.
- **Remove Task**: Select a task from the dropdown and click *Remove Task*.
- **Complete Task**: Select an incomplete task and click *Mark as Completed*.
- **List Tasks**: View all tasks, or filter by status.
- **Help**: This page.

**Data Persistence**

All tasks are stored in `tasks.json` in the same directory as this script.  
The file is updated atomically to prevent corruption.

**Error Handling**

- Empty descriptions are rejected.
- Invalid task IDs produce a friendly error message.
- Unexpected errors are displayed with a stack trace for debugging.

Enjoy managing your tasks!
"""
        st.markdown(help_text)

    # --------------------------------------------------------------------- #
    #  Footer
    # --------------------------------------------------------------------- #
    st.markdown("---")
    st.caption("© 2026 Todo List App – Streamlit UI")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        st.exception(f"Fatal error: {exc}")