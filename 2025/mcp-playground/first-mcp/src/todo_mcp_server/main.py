import asyncio
import json
import os
import sys
from typing import Optional

# Add the parent directory to the Python path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP

# Import with absolute path
try:
    from todo_mcp_server.todo_manager import TodoManager
except ImportError:
    from src.todo_mcp_server.todo_manager import TodoManager

mcp = FastMCP("todo-mcp-server")

# Global server instance
todo_server = None


class TodoMCPServer:
    """Todo List Management MCP Server"""

    def __init__(self):
        self.todo_manager = TodoManager()


def get_todo_manager():
    """Get or create the TodoManager instance"""
    global todo_server
    if todo_server is None:
        todo_server = TodoMCPServer()
    return todo_server.todo_manager


@mcp.tool()
def add_task(
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[str] = None,
) -> str:
    """Add a new todo task

    Args:
        title: Task title (required)
        description: Task description (optional)
        priority: Task priority (default: medium)
        due_date: Due date and time (YYYY-MM-DD HH:MM format, optional)
    """
    try:
        task = get_todo_manager().add_task(title, description, priority, due_date)

        response = f"✅ New task added successfully:\n"
        response += f"ID: {task.id}\n"
        response += f"Title: {task.title}\n"
        response += f"Priority: {task.priority}\n"
        if task.description:
            response += f"Description: {task.description}\n"
        if task.due_date:
            response += f"Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}\n"

        return response

    except Exception as e:
        return f"❌ Error occurred while adding task: {str(e)}"


@mcp.tool()
def list_tasks(filter: str = "all") -> str:
    """Display a list of todo tasks

    Args:
        fileter: Fileter for tasks to display (all, completed, pending, high, medium, low)
    """
    try:
        if filter == "completed":
            tasks = get_todo_manager().get_completed_tasks()
        elif filter == "pending":
            tasks = get_todo_manager().get_pending_tasks()
        elif filter in ["high", "medium", "low"]:
            tasks = get_todo_manager().get_tasks_by_priority(filter)
        else:  # "all"
            tasks = get_todo_manager().get_all_tasks()

        if not tasks:
            return "📝 No matching tasks found."

        response = f"📋 Todo List ({filter}):\n\n"

        for task in tasks:
            status = "✅" if task.completed else "⭕️"
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[task.priority]

            response += f"{status} [{task.id}] {priority_emoji} {task.title}\n"

            if task.description:
                response += f"    📄 {task.description}\n"

            if task.due_date:
                response += f"    ⏰ Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}\n"

            response += (
                f"    📅 Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            )

            if task.updated_at:
                response += (
                    f"    🔄 Updated: {task.updated_at.strftime('%Y-%m-%d %H:%M')}\n"
                )

            response += "\n"

        return response

    except Exception as e:
        return f"❌ Error occurred while retrieving task list: {str(e)}"


@mcp.tool()
def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
) -> str:
    """Update an existing todo task

    Args:
        tasks_id: ID of the task to update (required)
        title: New title (optional)
        description: New description (optional)
        priority: New priority (optional)
        due_date: New due date and time (optional)
    """
    try:
        task = get_todo_manager().update_task(
            task_id, title, description, priority, due_date
        )

        if task:
            return f"✅ Task ID {task_id} updated successfully."
        else:
            return f"❌ Task ID {task_id} not found."

    except Exception as e:
        return f"❌ Error occurred while updating task: {str(e)}"


@mcp.tool()
def complete_task(task_id: int) -> str:
    """Mark a task as completed

    Args:
        tasks_id: ID of the task to mark as completed
    """
    try:
        task = get_todo_manager().complete_task(task_id)

        if task:
            return f"🎉 Task '{task.title}' marked as completed!"
        else:
            return f"❌ Task ID {task_id} not found."

    except Exception as e:
        return f"❌ Error occurred while completing task: {str(e)}"


@mcp.tool()
def uncomplete_task(task_id: int) -> str:
    """Mark a task as incomplete

    Args:
        task_id: ID of the task to mark as incomplete
    """
    try:
        task = get_todo_manager().uncomplete_task(task_id)

        if task:
            return f"🔄 Task '{task.title}' marked as incomplete."
        else:
            return f"❌ Task ID {task_id} not found."

    except Exception as e:
        return f"❌ Error occurred while marking task as incomplete: {str(e)}"


@mcp.tool()
def delete_task(task_id: int) -> str:
    """Delete a task

    Args:
        task_id: ID of the task to delete
    """
    try:
        # Get task info before deletion
        task = get_todo_manager().get_task(task_id)
        if not task:
            return f"❌ Task ID {task_id} not found."

        task_title = task.title
        success = get_todo_manager().delete_task(task_id)

        if success:
            return f"🗑️ Task '{task_title}' deleted successfully"
        else:
            return f"❌ Failed to delete task."

    except Exception as e:
        return f"❌ Error occurred while deleteing task: {str(e)}"


@mcp.tool()
def get_task_stats() -> str:
    """Display task statistics"""

    try:
        stats = get_todo_manager().get_stats()

        response = "📊 Todo List Statistics:\n\n"
        response += f"📝 Total tasks: {stats['total_tasks']}\n"
        response += f"✅ Completed: {stats['completed_tasks']}\n"
        response += f"⭕ Pending: {stats['pending_tasks']}\n"
        response += f"📈 Completion rate: {stats['completion_rate']}%\n\n"
        response += f"🔴 High priority: {stats['high_priority']}\n"
        response += f"🟡 Medium priority: {stats['medium_priority']}\n"
        response += f"🟢 Low priority: {stats['low_priority']}\n"

        return response

    except Exception as e:
        return f"❌ Error occurred while retrieving statistics: {str(e)}"


def main():
    """Entry point"""
    mcp.run()


if __name__ == "__main__":
    main()
