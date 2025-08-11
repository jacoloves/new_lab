from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TodoItem(BaseModel):
    """ToDo Item Model"""

    id: int = Field(..., description="ToDo items unique id")
    title: str = Field(..., min_length=1, max_length=200, description="Task Title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Detail Explanation of Task"
    )
    completed: bool = Field(default=False, description="complete state")
    priority: str = Field(
        default="medium", pattern="^(low|medium|high)$", description="prority"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="created_at")
    updated_at: Optional[datetime] = Field(None, description="updated_at")
    due_date: Optional[datetime] = Field(None, description="due_date")

    def mark_completed(self) -> None:
        """Mark the task as complete and set the update date and time."""
        self.completed = True
        self.updated_at = datetime.now()

    def mark_incomplete(self) -> None:
        """Mark the task as incomplete and set the update date and time."""
        self.completed = False
        self.updated_at = datetime.now()

    def update_info(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[datetime] = None,
    ) -> None:
        """Update task information"""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if priority is not None and priority in ["low", "medium", "high"]:
            self.priority = priority
        if due_date is not None:
            self.due_date = due_date
        self.updated_at = datetime.now()


class TodoList(BaseModel):
    """ToDo List Model"""

    tasks: List[TodoItem] = Field(default_factory=list, description="List of TodoItem")

    def add_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[datetime] = None,
    ) -> TodoItem:
        """add new Tasks"""
        new_id = max([task.id for task in self.tasks], default=0) + 1

        task = TodoItem(
            id=new_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
        self.tasks.append(task)
        return task

    def get_task(self, task_id: int) -> Optional[TodoItem]:
        """Get tasks by ID"""
        return next((task for task in self.tasks if task.id == task_id), None)

    def remove_task(self, task_id: int) -> bool:
        """Delete tasks"""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False

    def get_completed_tasks(self) -> List[TodoItem]:
        """Get tasks by completed"""
        return [task for task in self.tasks if task.completed]

    def get_pending_tasks(self) -> List[TodoItem]:
        """Get tasks by incomplete"""
        return [task for task in self.tasks if not task.completed]

    def get_tasks_by_priority(self, priority: str) -> List[TodoItem]:
        """Get tasks by priority"""
        return [task for task in self.tasks if task.priority == priority]
