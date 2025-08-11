import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from todo_mcp_server.models import TodoList, TodoItem


class TodoManager:
    """Class responsible for managing the ToDo list and JSON persistence"""

    def __init__(self, data_file: str = "data/todos.json"):
        """
        Init TodoManager

        Args:
            data_file: Path to the JSON file that stores the ToDo data
        """
        self.data_file = Path(data_file)
        self.todo_list = TodoList()
        self._ensure_date_directory()
        self._load_data()

    def _ensure_date_directory(self) -> None:
        """Confirm that the data directory exists"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_data(self) -> None:
        """Read data from a JSON file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._convert_datetime_string(data)
                    self.todo_list = TodoList(**data)
            else:
                self.todo_list = TodoList()
                self._save_data()
        except (json.JSONDecodeError, Exception) as e:
            print(f"data loading error: {e}")
            self.todo_list = TodoList()
            self._save_data()

    def _convert_datetime_string(self, data: dict) -> None:
        """Convert datetime strings in the dictionary to datetime objects"""
        if "tasks" in data:
            for task in data["tasks"]:
                for field in ["cretaed_at", "updated_at", "due_date"]:
                    if field in task and task[field]:
                        try:
                            task[field] = datetime.fromisoformat(
                                task[field].replace("Z", "+00:00")
                            )
                        except (ValueError, AttributeError):
                            task[field] = None

    def _save_data(self) -> None:
        """Save current data to a JSON file"""
        try:
            data = json.loads(self.todo_list.model_dump_json())

            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"data storage error: {e}")
            raise

    def add_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[str] = None,
    ) -> TodoItem:
        """Add new tasks"""
        due_datetime = None
        if due_date:
            try:
                due_datetime = datetime.fromisoformat(due_date)
            except ValueError:
                pass

        task = self.todo_list.add_task(title, description, priority, due_datetime)
        self._save_data()
        return task

    def get_all_tasks(self) -> List[TodoItem]:
        """Get all tasks"""
        return self.todo_list.tasks

    def get_task(self, task_id: int) -> Optional[TodoItem]:
        """Get tasks with the specified ID"""
        return self.todo_list.get_task(task_id)

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Optional[TodoItem]:
        """Update task information"""
        task = self.todo_list.get_task(task_id)
        if task:
            due_datetime = None
            if due_date:
                try:
                    due_datetime = datetime.fromisoformat(due_date)
                except ValueError:
                    pass

            task.update_info(title, description, priority, due_datetime)
            self._save_data()
            return task
        return None

    def complete_task(self, task_id: int) -> Optional[TodoItem]:
        """Complete task"""
        task = self.todo_list.get_task(task_id)
        if task:
            task.mark_completed()
            self._save_data()
            return task
        return None

    def uncomplete_task(self, task_id: int) -> Optional[TodoItem]:
        """Uncomplete task"""
        task = self.todo_list.get_task(task_id)
        if task:
            task.mark_incomplete()
            self._save_data()
            return task
        return None

    def delete_task(self, task_id: int) -> bool:
        """Delete tasks"""
        if self.todo_list.remove_task(task_id):
            self._save_data()
            return True
        return False

    def get_completed_tasks(self) -> List[TodoItem]:
        """Get completed task"""
        return self.todo_list.get_completed_tasks()

    def get_pending_tasks(self) -> List[TodoItem]:
        """Get pending task"""
        return self.todo_list.get_pending_tasks()

    def get_tasks_by_priority(self, priority: str) -> List[TodoItem]:
        """Get tasks by priority"""
        return self.todo_list.get_tasks_by_priority(priority)

    def get_stats(self) -> dict:
        """Get stats"""
        all_tasks = self.todo_list.tasks
        completed = len(self.get_completed_tasks())
        pending = len(self.get_pending_tasks())

        return {
            "total_tasks": len(all_tasks),
            "completed_task": completed,
            "pending_tasks": pending,
            "completion_rate": round(completed / len(all_tasks) * 100, 1)
            if all_tasks
            else 0,
            "high_priority": len(self.get_tasks_by_priority("high")),
            "medium_priority": len(self.get_tasks_by_priority("medium")),
            "low_priority": len(self.get_tasks_by_priority("low")),
        }
