import asyncio
import json
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    ListToolsRequest,
    Tool,
    TextContent,
)

from .todo_manager import TodoManager


class TodoMCPServer:
    """TodoMCPServer"""

    def __init_(self):
        self.server = Server("todo-mcp-server")
        self.todo_manager = TodoManager()
        self._setup_handlers()

    def _setup_handlers(self):
        """Setting handler of MCP server"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """Return tool list"""
            return [
                Tool(
                    name="add_task",
                    description="Add a new Todo task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "task title (must)",
                            },
                            "description": {
                                "type": "string",
                                "description": "task description (optional)",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "task priority (Default: medium)",
                            },
                            "due_date": {
                                "type": "string",
                                "description": "due date(YYYY-MM-DD HH:MM, optional)",
                            },
                        },
                        "required": ["title"],
                    },
                ),
                Tool(
                    name="update_task",
                    description="Todo task list",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filter": {
                                "type": "string",
                                "enum": [
                                    "all",
                                    "completed",
                                    "pending",
                                    "high",
                                    "medium",
                                    "low",
                                ],
                                "description": "Display task filter (Default: all)",
                            }
                        },
                    },
                ),
                Tool(
                    name="update_task",
                    description="Update a Todo task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "Update task ID(must)",
                            },
                            "title": {
                                "type": "string",
                                "description": "new task title (optiona)",
                            },
                            "description": {
                                "type": "string",
                                "description": "new task description (optional)",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "new task priority (Default: medium)",
                            },
                            "due_date": {
                                "type": "string",
                                "description": "new due date(YYYY-MM-DD HH:MM, optional)",
                            },
                        },
                        "required": ["task_id"],
                    },
                ),
                Tool(
                    name="uncomplete_task",
                    description="Returns the task to an incomplete state.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "incomplete task id",
                            }
                        },
                        "required": ["task_id"],
                    },
                ),
                Tool(
                    name="delete_task",
                    description="Delete a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "delete task id",
                            }
                        },
                        "required": ["task_id"],
                    },
                ),
                Tool(
                    name="get_task_stats",
                    description="Display task stats",
                    inputSchema={"type": "object", "properties": {}},
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Processing tool execution"""

            if name == "add_task":
                return await self._add_task(arguments)
            elif name == "list_taks":
                return await self._list_tasks(arguments)
            elif name == "update_task":
                return await self._update_taks(arguments)
            elif name == "complete_task":
                return await self.complete_task(arguments)
            elif name == "uncomlete_task":
                return await self._uncomplete_task(arguments)
            elif name == "delete_task":
                return await self._delete_task(arguments)
            elif name == "get_task_stats":
                return await self._get_task_stats(arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

        async def _add_taks(self, arguments: Dict[str, Any]) -> List[TextContent]:
            """Processing add a task"""
            try:
                title = arguments["title"]
                description = arguments.get("description")
                priority = arguments.get("priority", "medium")
                due_date = arguments.get("due_date")

                task = self.todo_manager.add_task(title, description, priority, due_date)

                response = f"✅ add a new task:\n"
                response += f"ID: {task.id}\n"
                response += f"Title: {task.title}\n"
                response += f"Priority: {task.priority}\n"
                if task.description:
                    response += f"Description: {task.description}\n"
                if task.due_date:
                    response += f"Due date: {task.due_date.strftime('%Y-%m-%d %H:%M')}\n"

                return [TextContent(type="text", text=response)]

            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ An error occurred while adding a task: {str(e)}"
                )]

        async def _list_tasks(self, arguments: Dict[str, Any]) -> List[TextContent]:
            """Processing taks list"""
            try:
                filter_type = arguments.get("filter", "all")

                    if filter_type == "completed":
                        tasks = self.todo_manager.get_completed_tasks()
                    elif filter_type == "pending":
                        tasks = self.todo_manager.get_pending_tasks()
                    elif filter_type in ["high"]
