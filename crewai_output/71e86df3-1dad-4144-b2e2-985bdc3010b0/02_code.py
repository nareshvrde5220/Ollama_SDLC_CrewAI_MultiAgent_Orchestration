# Phase UUID: a21af5c8-4589-49ae-a1d5-2e1983ae233e

#!/usr/bin/env python3
"""
Todo List CLI Application

A lightweight command-line tool for managing a personal to-do list.
All data is persisted in a JSON file, ensuring that the task list survives across sessions.
"""

import json
import os
import sys
from typing import List, Dict, Optional, Any
from pathlib import Path


class TodoList:
    """
    A class to manage a todo list with persistence to a JSON file.
    
    This class handles adding, removing, completing, and listing tasks,
    with automatic persistence to a JSON file.
    """
    
    def __init__(self, filename: str = "tasks.json"):
        """
        Initialize the TodoList with a filename for persistence.
        
        Args:
            filename: The name of the JSON file to store tasks.
        """
        self.filename = filename
        self.tasks: List[Dict[str, Any]] = []
        self._load_tasks()
    
    def _load_tasks(self) -> None:
        """Load tasks from the JSON file."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as file:
                    self.tasks = json.load(file)
            else:
                self.tasks = []
        except (json.JSONDecodeError, IOError) as e:
            raise RuntimeError(f"Failed to load tasks from {self.filename}: {e}")
    
    def _save_tasks(self) -> None:
        """
        Save tasks to the JSON file using atomic write.
        
        This method writes to a temporary file first, then renames it to
        ensure data integrity in case of crashes.
        """
        temp_filename = f"{self.filename}.tmp"
        try:
            with open(temp_filename, 'w', encoding='utf-8') as file:
                json.dump(self.tasks, file, indent=2)
            os.replace(temp_filename, self.filename)
        except (IOError, OSError) as e:
            raise RuntimeError(f"Failed to save tasks to {self.filename}: {e}")
    
    def _get_next_id(self) -> int:
        """
        Get the next available task ID.
        
        Returns:
            The next available integer ID.
        """
        if not self.tasks:
            return 1
        return max(task['id'] for task in self.tasks) + 1
    
    def add_task(self, description: str) -> int:
        """
        Add a new task to the list.
        
        Args:
            description: The description of the task.
            
        Returns:
            The ID of the newly added task.
            
        Raises:
            ValueError: If the description is empty.
        """
        if not description.strip():
            raise ValueError("Task description cannot be empty.")
        
        task_id = self._get_next_id()
        task = {
            "id": task_id,
            "description": description,
            "completed": False
        }
        self.tasks.append(task)
        self._save_tasks()
        return task_id
    
    def remove_task(self, task_id: int) -> bool:
        """
        Remove a task from the list.
        
        Args:
            task_id: The ID of the task to remove.
            
        Returns:
            True if the task was removed, False if not found.
        """
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                del self.tasks[i]
                self._save_tasks()
                return True
        return False
    
    def complete_task(self, task_id: int) -> bool:
        """
        Mark a task as complete.
        
        Args:
            task_id: The ID of the task to complete.
            
        Returns:
            True if the task was marked complete, False if not found.
        """
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                self._save_tasks()
                return True
        return False
    
    def list_tasks(self, filter_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all tasks or filter by completion status.
        
        Args:
            filter_status: Optional filter ('completed', 'incomplete', or None for all).
            
        Returns:
            A list of tasks matching the filter criteria.
        """
        if filter_status is None:
            return self.tasks
        
        if filter_status == 'completed':
            return [task for task in self.tasks if task['completed']]
        elif filter_status == 'incomplete':
            return [task for task in self.tasks if not task['completed']]
        else:
            raise ValueError("Invalid filter status. Use 'completed', 'incomplete', or None.")
    
    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific task by ID.
        
        Args:
            task_id: The ID of the task to retrieve.
            
        Returns:
            The task dictionary if found, None otherwise.
        """
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None


def print_help() -> None:
    """Print the help message with available commands."""
    help_text = """
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
"""
    print(help_text)


def parse_command(args: List[str]) -> tuple:
    """
    Parse command line arguments.
    
    Args:
        args: List of command line arguments.
        
    Returns:
        Tuple of (command, arguments).
    """
    if not args:
        return "", []
    
    command = args[0].lower()
    return command, args[1:]


def main() -> None:
    """Main entry point for the Todo List CLI application."""
    todo_list = TodoList()
    
    print("Todo List CLI Application")
    print("=" * 30)
    
    while True:
        try:
            user_input = input("\n> ").strip()
            if not user_input:
                continue
                
            args = user_input.split()
            command, cmd_args = parse_command(args)
            
            if command in ['exit', 'quit']:
                print("Goodbye!")
                break
            elif command == 'help':
                print_help()
            elif command == 'add':
                if not cmd_args:
                    print("Error: Task description cannot be empty.")
                    continue
                description = ' '.join(cmd_args)
                try:
                    task_id = todo_list.add_task(description)
                    print(f"Task added: {task_id} {description}")
                except ValueError as e:
                    print(f"Error: {e}")
            elif command == 'remove':
                if not cmd_args:
                    print("Error: Please provide a task ID to remove.")
                    continue
                try:
                    task_id = int(cmd_args[0])
                    task = todo_list.get_task(task_id)
                    if task:
                        todo_list.remove_task(task_id)
                        print(f"Task removed: {task_id} {task['description']}")
                    else:
                        print(f"Error: Task ID {task_id} does not exist.")
                except ValueError:
                    print("Error: Task ID must be an integer.")
            elif command == 'complete':
                if not cmd_args:
                    print("Error: Please provide a task ID to complete.")
                    continue
                try:
                    task_id = int(cmd_args[0])
                    task = todo_list.get_task(task_id)
                    if task:
                        todo_list.complete_task(task_id)
                        print(f"Task completed: {task_id} {task['description']}")
                    else:
                        print(f"Error: Task ID {task_id} does not exist.")
                except ValueError:
                    print("Error: Task ID must be an integer.")
            elif command == 'list':
                try:
                    filter_status = None
                    if cmd_args:
                        if cmd_args[0] == '--all':
                            filter_status = None
                        elif cmd_args[0] == '--completed':
                            filter_status = 'completed'
                        elif cmd_args[0] == '--incomplete':
                            filter_status = 'incomplete'
                        else:
                            print("Error: Unknown filter. Use --all, --completed, or --incomplete.")
                            continue
                    
                    tasks = todo_list.list_tasks(filter_status)
                    if not tasks:
                        status_text = ""
                        if filter_status == 'completed':
                            status_text = " (completed)"
                        elif filter_status == 'incomplete':
                            status_text = " (incomplete)"
                        print(f"No tasks{status_text}.")
                    else:
                        for task in tasks:
                            status = "✓" if task['completed'] else "○"
                            print(f"{status} [{task['id']}] {task['description']}")
                except ValueError as e:
                    print(f"Error: {e}")
            else:
                print("Error: Unknown command. Type 'help' for a list of commands.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()