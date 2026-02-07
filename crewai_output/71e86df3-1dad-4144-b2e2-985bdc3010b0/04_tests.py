# Phase UUID: ca2ca062-a6f1-4036-9a92-ba7fd61a8929

import json
import os
import tempfile
import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

# Import the module to test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from todo_list import TodoList, print_help, parse_command, main


@pytest.fixture
def temp_todo_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('[]')
        temp_file = f.name
    
    yield temp_file
    
    # Clean up
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def todo_list_with_file(temp_todo_file):
    """Create a TodoList instance with a temporary file."""
    return TodoList(filename=temp_todo_file)


class TestTodoList:
    """Test cases for the TodoList class."""
    
    def test_init_creates_empty_tasks(self, temp_todo_file):
        """Test that initialization creates an empty task list."""
        todo_list = TodoList(filename=temp_todo_file)
        assert todo_list.tasks == []
    
    def test_init_loads_existing_tasks(self, temp_todo_file):
        """Test that initialization loads existing tasks from file."""
        # Write some initial data
        initial_data = [
            {"id": 1, "description": "Test task 1", "completed": False},
            {"id": 2, "description": "Test task 2", "completed": True}
        ]
        
        with open(temp_todo_file, 'w') as f:
            json.dump(initial_data, f)
        
        todo_list = TodoList(filename=temp_todo_file)
        assert todo_list.tasks == initial_data
    
    def test_load_tasks_handles_missing_file(self, temp_todo_file):
        """Test that loading tasks from a missing file creates empty list."""
        # Ensure file doesn't exist
        if os.path.exists(temp_todo_file):
            os.unlink(temp_todo_file)
        
        todo_list = TodoList(filename=temp_todo_file)
        assert todo_list.tasks == []
    
    def test_load_tasks_handles_corrupted_json(self, temp_todo_file):
        """Test that loading tasks from corrupted JSON raises RuntimeError."""
        with open(temp_todo_file, 'w') as f:
            f.write('{"invalid": json}')
        
        with pytest.raises(RuntimeError):
            TodoList(filename=temp_todo_file)
    
    def test_save_tasks_atomic_write(self, temp_todo_file):
        """Test that save_tasks uses atomic write."""
        todo_list = TodoList(filename=temp_todo_file)
        todo_list.tasks = [
            {"id": 1, "description": "Test task", "completed": False}
        ]
        
        # Mock os.replace to verify it's called
        with patch('os.replace') as mock_replace:
            todo_list._save_tasks()
            mock_replace.assert_called_once()
    
    def test_save_tasks_handles_io_error(self, temp_todo_file):
        """Test that save_tasks handles IO errors."""
        todo_list = TodoList(filename=temp_todo_file)
        todo_list.tasks = [
            {"id": 1, "description": "Test task", "completed": False}
        ]
        
        # Mock os.replace to raise an exception
        with patch('os.replace') as mock_replace:
            mock_replace.side_effect = OSError("Test error")
            with pytest.raises(RuntimeError):
                todo_list._save_tasks()
    
    def test_get_next_id_empty_list(self, todo_list_with_file):
        """Test that get_next_id returns 1 for empty list."""
        assert todo_list_with_file._get_next_id() == 1
    
    def test_get_next_id_with_existing_tasks(self, todo_list_with_file):
        """Test that get_next_id returns correct ID for existing tasks."""
        todo_list_with_file.tasks = [
            {"id": 1, "description": "Task 1", "completed": False},
            {"id": 3, "description": "Task 3", "completed": False}
        ]
        assert todo_list_with_file._get_next_id() == 4
    
    def test_add_task_valid_description(self, todo_list_with_file):
        """Test that add_task adds a valid task."""
        task_id = todo_list_with_file.add_task("Test task")
        assert task_id == 1
        assert len(todo_list_with_file.tasks) == 1
        assert todo_list_with_file.tasks[0]['id'] == 1
        assert todo_list_with_file.tasks[0]['description'] == "Test task"
        assert todo_list_with_file.tasks[0]['completed'] is False
    
    def test_add_task_empty_description_raises_value_error(self, todo_list_with_file):
        """Test that add_task raises ValueError for empty description."""
        with pytest.raises(ValueError, match="Task description cannot be empty."):
            todo_list_with_file.add_task("")
    
    def test_add_task_whitespace_description_raises_value_error(self, todo_list_with_file):
        """Test that add_task raises ValueError for whitespace-only description."""
        with pytest.raises(ValueError, match="Task description cannot be empty."):
            todo_list_with_file.add_task("   ")
    
    def test_remove_task_existing_task(self, todo_list_with_file):
        """Test that remove_task removes an existing task."""
        # Add a task first
        task_id = todo_list_with_file.add_task("Test task")
        assert len(todo_list_with_file.tasks) == 1
        
        # Remove it
        result = todo_list_with_file.remove_task(task_id)
        assert result is True
        assert len(todo_list_with_file.tasks) == 0
    
    def test_remove_task_nonexistent_task(self, todo_list_with_file):
        """Test that remove_task returns False for nonexistent task."""
        result = todo_list_with_file.remove_task(999)
        assert result is False
        assert len(todo_list_with_file.tasks) == 0
    
    def test_complete_task_existing_task(self, todo_list_with_file):
        """Test that complete_task marks an existing task as complete."""
        # Add a task first
        task_id = todo_list_with_file.add_task("Test task")
        assert todo_list_with_file.tasks[0]['completed'] is False
        
        # Complete it
        result = todo_list_with_file.complete_task(task_id)
        assert result is True
        assert todo_list_with_file.tasks[0]['completed'] is True
    
    def test_complete_task_nonexistent_task(self, todo_list_with_file):
        """Test that complete_task returns False for nonexistent task."""
        result = todo_list_with_file.complete_task(999)
        assert result is False
        assert len(todo_list_with_file.tasks) == 0
    
    def test_list_tasks_all(self, todo_list_with_file):
        """Test that list_tasks returns all tasks when no filter."""
        todo_list_with_file.tasks = [
            {"id": 1, "description": "Task 1", "completed": False},
            {"id": 2, "description": "Task 2", "completed": True}
        ]
        result = todo_list_with_file.list_tasks()
        assert result == todo_list_with_file.tasks
    
    def test_list_tasks_completed(self, todo_list_with_file):
        """Test that list_tasks filters completed tasks."""
        todo_list_with_file.tasks = [
            {"id": 1, "description": "Task 1", "completed": False},
            {"id": 2, "description": "Task 2", "completed": True}
        ]
        result = todo_list_with_file.list_tasks('completed')
        assert len(result) == 1
        assert result[0]['id'] == 2
    
    def test_list_tasks_incomplete(self, todo_list_with_file):
        """Test that list_tasks filters incomplete tasks."""
        todo_list_with_file.tasks = [
            {"id": 1, "description": "Task 1", "completed": False},
            {"id": 2, "description": "Task 2", "completed": True}
        ]
        result = todo_list_with_file.list_tasks('incomplete')
        assert len(result) == 1
        assert result[0]['id'] == 1
    
    def test_list_tasks_invalid_filter(self, todo_list_with_file):
        """Test that list_tasks raises ValueError for invalid filter."""
        with pytest.raises(ValueError, match="Invalid filter status"):
            todo_list_with_file.list_tasks('invalid')
    
    def test_get_task_existing_task(self, todo_list_with_file):
        """Test that get_task returns existing task."""
        task_id = todo_list_with_file.add_task("Test task")
        task = todo_list_with_file.get_task(task_id)
        assert task is not None
        assert task['id'] == task_id
        assert task['description'] == "Test task"
    
    def test_get_task_nonexistent_task(self, todo_list_with_file):
        """Test that get_task returns None for nonexistent task."""
        task = todo_list_with_file.get_task(999)
        assert task is None


class TestHelperFunctions:
    """Test cases for helper functions."""
    
    def test_print_help(self):
        """Test that print_help prints the correct help text."""
        # Just make sure it doesn't crash
        print_help()
    
    def test_parse_command_empty_args(self):
        """Test that parse_command handles empty args."""
        command, args = parse_command([])
        assert command == ""
        assert args == []
    
    def test_parse_command_single_command(self):
        """Test that parse_command parses single command."""
        command, args = parse_command(["add"])
        assert command == "add"
        assert args == []
    
    def test_parse_command_with_args(self):
        """Test that parse_command parses command with arguments."""
        command, args = parse_command(["add", "buy", "groceries"])
        assert command == "add"
        assert args == ["buy", "groceries"]


class TestMainFunction:
    """Test cases for the main function."""
    
    @patch('todo_list.TodoList')
    @patch('todo_list.print_help')
    @patch('todo_list.parse_command')
    @patch('sys.stdin.readline')
    def test_main_exit_command(self, mock_readline, mock_parse_command, mock_print_help, mock_todo_list):
        """Test that main exits on exit command."""
        mock_readline.return_value = "exit\n"
        mock_parse_command.return_value = ("exit", [])
        mock_todo_list_instance = mock_todo_list.return_value
        mock_todo_list_instance.tasks = []
        
        with pytest.raises(SystemExit):
            main()
    
    @patch('todo_list.TodoList')
    @patch('todo_list.print_help')
    @patch('todo_list.parse_command')
    @patch('sys.stdin.readline')
    def test_main_help_command(self, mock_readline, mock_parse_command, mock_print_help, mock_todo_list):
        """Test that main handles help command."""
        mock_readline.return_value = "help\n"
        mock_parse_command.return_value = ("help", [])
        mock_todo_list_instance = mock_todo_list.return_value
        mock_todo_list_instance.tasks = []
        
        # This should not raise an exception
        main()
        mock_print_help.assert_called_once()
    
    @patch('todo_list.TodoList')
    @patch('todo_list.print_help')
    @patch('todo_list.parse_command')
    @patch('sys.stdin.readline')
    def test_main_add_command(self, mock_readline, mock_parse_command, mock_print_help, mock_todo_list):
        """Test that main handles add command."""
        mock_readline.return_value = "add Buy groceries\n"
        mock_parse_command.return_value = ("add", ["Buy", "groceries"])
        mock_todo_list_instance = mock_todo_list.return_value
        mock_todo_list_instance.tasks = []
        mock_todo_list_instance.add_task.return_value = 1
        
        # This should not raise an exception
        main()
        mock_todo_list_instance.add_task.assert_called_once_with("Buy groceries")
    
    @patch('todo_list.TodoList')
    @patch('todo_list.print_help')
    @patch('todo_list.parse_command')
    @patch('sys.stdin.readline')
    def test_main_remove_command(self, mock_readline, mock_parse_command, mock_print_help, mock_todo_list):
        """Test that main handles remove command."""
        mock_readline.return_value = "remove 1\n"
        mock_parse_command.return_value = ("remove", ["1"])
        mock_todo_list_instance = mock_todo_list.return_value
        mock_todo_list_instance.tasks = []
        mock_todo_list_instance.get_task.return_value = {"id": 1, "description": "Test task"}
        
        # This should not raise an exception
        main()
        mock_todo_list_instance.remove_task.assert_called_once_with(1)
    
    @patch('todo_list.TodoList')
    @patch('todo_list.print_help')
    @patch('todo_list.parse_command')
    @patch('sys.stdin.readline')
    def test_main_complete_command(self, mock_readline, mock_parse_command, mock_print_help, mock_todo_list):
        """Test that main handles complete command."""
        mock_readline.return_value = "complete 1\n"
        mock_parse_command.return_value = ("complete", ["1"])
        mock_todo_list_instance = mock_todo_list.return_value
        mock_todo_list_instance.tasks = []
        mock_todo_list_instance.get_task.return_value = {"id": 1, "description": "Test task"}
        
        # This should not raise an exception
        main()
        mock_todo_list_instance.complete_task.assert_called_once_with(1)
    
    @patch('todo_list.TodoList')
    @patch('todo_list.print_help')
    @patch('todo_list.parse_command')
    @patch('sys.stdin.readline')
    def test_main_list_command(self, mock_readline, mock_parse_command, mock_print_help, mock_todo_list):
        """Test that main handles list command."""
        mock_readline.return_value = "list\n"
        mock_parse_command.return_value = ("list", [])
        mock_todo_list_instance = mock_todo_list.return_value
        mock_todo_list_instance.tasks = []
        
        # This should not raise an exception
        main()
        mock_todo_list_instance.list_tasks.assert_called_once_with(None)
    
    @patch('todo_list.TodoList')
    @patch('todo_list.print_help')
    @patch('todo_list.parse_command')
    @patch('sys.stdin.readline')
    def test_main_unknown_command(self, mock_readline, mock_parse_command, mock_print_help, mock_todo_list):
        """Test that main handles unknown command."""
        mock_readline.return_value = "unknown\n"
        mock_parse_command.return_value = ("unknown", [])
        mock_todo_list_instance = mock_todo_list.return_value
        mock_todo_list_instance.tasks = []
        
        # This should not raise an exception
        main()
    
    @patch('todo_list.TodoList')
    @patch('todo_list.print_help')
    @patch('todo_list.parse_command')
    @patch('sys.stdin.readline')
    def test_main_keyboard_interrupt(self, mock_readline, mock_parse_command, mock_print_help, mock_todo_list):
        """Test that main handles keyboard interrupt."""
        mock_readline.side_effect = KeyboardInterrupt()
        mock_todo_list_instance = mock_todo_list.return_value
        mock_todo_list_instance.tasks = []
        
        # This should not raise an exception
        main()
    
    @patch('todo_list.TodoList')
    @patch('todo_list.print_help')
    @patch('todo_list.parse_command')
    @patch('sys.stdin.readline')
    def test_main_eof_error(self, mock_readline, mock_parse_command, mock_print_help, mock_todo_list):
        """Test that main handles EOF error."""
        mock_readline.side_effect = EOFError()
        mock_todo_list_instance = mock_todo_list.return_value
        mock_todo_list_instance.tasks = []
        
        # This should not raise an exception
        main()


def test_integration_complete_workflow():
    """Test a complete workflow of adding, completing, and listing tasks."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('[]')
        temp_file = f.name
    
    try:
        todo_list = TodoList(filename=temp_file)
        
        # Add tasks
        task1_id = todo_list.add_task("Buy groceries")
        task2_id = todo_list.add_task("Walk the dog")
        
        # Verify tasks were added
        assert len(todo_list.tasks) == 2
        assert todo_list.tasks[0]['id'] == task1_id
        assert todo_list.tasks[1]['id'] == task2_id
        
        # Complete one task
        todo_list.complete_task(task1_id)
        
        # Verify completion
        assert todo_list.tasks[0]['completed'] is True
        assert todo_list.tasks[1]['completed'] is False
        
        # List all tasks
        all_tasks = todo_list.list_tasks()
        assert len(all_tasks) == 2
        
        # List completed tasks
        completed_tasks = todo_list.list_tasks('completed')
        assert len(completed_tasks) == 1
        assert completed_tasks[0]['id'] == task1_id
        
        # List incomplete tasks
        incomplete_tasks = todo_list.list_tasks('incomplete')
        assert len(incomplete_tasks) == 1
        assert incomplete_tasks[0]['id'] == task2_id
        
        # Remove a task
        todo_list.remove_task(task2_id)
        
        # Verify removal
        assert len(todo_list.tasks) == 1
        assert todo_list.tasks[0]['id'] == task1_id
        
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_edge_cases():
    """Test edge cases for the TodoList."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('[]')
        temp_file = f.name
    
    try:
        todo_list = TodoList(filename=temp_file)
        
        # Test adding many tasks
        for i in range(100):
            todo_list.add_task(f"Task {i}")
        
        assert len(todo_list.tasks) == 100
        assert todo_list.tasks[0]['id'] == 1
        assert todo_list.tasks[-1]['id'] == 100
        
        # Test removing tasks in different orders
        todo_list.remove_task(1)
        todo_list.remove_task(50)
        todo_list.remove_task(100)
        
        assert len(todo_list.tasks) == 97
        assert todo_list.tasks[0]['id'] == 2
        assert todo_list.tasks[-1]['id'] == 99
        
        # Test completing tasks
        todo_list.complete_task(2)
        todo_list.complete_task(99)
        
        assert todo_list.tasks[0]['completed'] is True
        assert todo_list.tasks[-1]['completed'] is True
        
        # Test listing with no tasks
        todo_list.tasks = []
        assert len(todo_list.list_tasks()) == 0
        assert len(todo_list.list_tasks('completed')) == 0
        assert len(todo_list.list_tasks('incomplete')) == 0
        
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)