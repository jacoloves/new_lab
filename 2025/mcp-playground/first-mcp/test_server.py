#!/usr/bin/env python3
"""Simple test script for the Todo MCP Server"""

import asyncio
from src.todo_mcp_server.todo_manager import TodoManager
from todo_mcp_server.main import get_todo_manager


async def test_todo_manager():
    """Test TodoManager basic functionality"""
    print("🧪 Testing TodoManager...")

    # Initialize manager with clean test data
    import os

    test_file = "test_data/todos.json"
    if os.path.exists(test_file):
        os.remove(test_file)

    # Initialize manager
    manager = TodoManager(test_file)

    # Add some test tasks
    print("\n📝 Adding test tasks...")
    task1 = manager.add_task(
        "Buy groceries", "Milk, bread, eggs", "high", "2025-08-11 9:00"
    )
    task2 = manager.add_task(
        "Write documentatios", "Complete the project docs", "medium"
    )
    task3 = manager.add_task("Call mom", priority="low")

    print(f"✅ Added task 1: {task1.title} (ID: {task1.id})")
    print(f"✅ Added task 2: {task2.title} (ID: {task2.id})")
    print(f"✅ Added task 3: {task3.title} (ID: {task3.id})")

    # List all tasks
    print("\n📋 All tasks:")
    all_tasks = manager.get_all_tasks()
    for task in all_tasks:
        status = "✅" if task.completed else "⭕️"
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[task.priority]
        print(f"   {status} [{task.id}] {priority_emoji} {task.title}")

    # Complete a task
    print("\n🎉 Completing task 1...")
    completed_task = manager.complete_task(1)
    if completed_task:
        print(f"✅ Task '{completed_task.title}' marked as completed!")

    # Get statistics
    print("\n📊 Statistics:")
    try:
        stats = manager.get_stats()
        print(f"   Total: {stats['total_tasks']}")
        print(f"   Completed: {stats['completed_tasks']}")
        print(f"   Pending: {stats['pending_tasks']}")
        print(f"   Completion rate: {stats['completion_rate']}%")

    except Exception as e:
        print(f"   ❌ Error getting stats: {e}")
        print(
            f"   Debug - Available keys: {list(stats.keys()) if 'stats' in locals() else 'stats not defined'}"
        )
        raise

    # Test filetering
    print("\n🔍 Pending tasks:")
    pending = manager.get_pending_tasks()
    for task in pending:
        print(f"   ⭕️ [{task.id}] {task.title}")

    print("\n✅ TodoManager test completed!")


async def test_server_import():
    """Test server import and basic initialize"""
    print("\n🧪 Testing server import...")

    try:
        from src.todo_mcp_server.main import TodoMCPServer, mcp, todo_server

        print("✅ Server import successful")

        server = TodoMCPServer()
        print("✅ Server initialization successful")

        # Test that server has the expected attributes for FastMCP
        assert hasattr(
            server, "todo_manager"
        ), "Server should have 'todo_manager' attribute"
        print("✅ Server attributes check passed")

        # Test that FastMCP instance exists
        assert mcp is not None, "FastMCP instance should exist"
        print("✅ FastMCP instance check passed")

        # Test that todo manager can be accessed through function
        todo_manager = get_todo_manager()
        assert todo_manager is not None, "TodoManager should be accessible"
        assert hasattr(
            todo_manager, "add_task"
        ), "TodoManager should have 'add_task' method"
        print("✅ TodoManager access check passed")

    except Exception as e:
        print(f"❌ Server test failed: {e}")
        raise


async def test_tools_functionality():
    """Test the MCP tools functionality"""
    print("\n🧪 Testing MCP tools...")

    try:
        from src.todo_mcp_server.main import (
            add_task,
            list_tasks,
            complete_task,
            get_task_stats,
        )

        print("✅ Tool imports successful")

        # Test add_task
        result = add_task("Test task", "This is a test", "high")
        assert "New task added successfully" in result, f"Add task failed: {result}"
        print("✅ add_tasks works")

        # Test list_tasks
        result = list_tasks("all")
        assert "Todo List" in result, f"List tasks failed: {result}"
        print("✅ list_tasks works")

        # Test get_task_stats
        result = get_task_stats()
        assert "Todo List Statistics" in result, f"Get stats failed: {result}"
        print("✅ get_task_stats works")

        # Test complete_task (assuming task ID 1 exists)
        result = complete_task(1)
        assert (
            "marked as completed" in result or "not found" in result
        ), f"Complete task failed: {result}"
        print("✅ complete_task works")

        print("✅ All tools functionality tests passed!")

    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        raise


async def test_fastmcp_setup():
    """Test FastMCP setup and tool registration"""
    print("\n🧪 Testing FastMCP setup...")

    try:
        from src.todo_mcp_server.main import mcp

        # Check if tools are registerd (this is internal to FastMCP,
        # so we'll just verify the mcp object exists and has expected attributes)
        assert hasattr(mcp, "run"), "FastMCP should have 'run' method"
        print("✅ FastMCP has run method")

        assert hasattr(mcp, "tool"), "FastMCP should have 'tool' decorator"
        print("✅ FastMCP has tool decorator")

        print("✅ FastMCP setup test passed!")

    except Exception as e:
        print(f"❌ FastMCP setup test failed: {e}")
        raise


async def main():
    """Run all tests"""
    print("🚀 Starting Todo MCP Server Tests\n")

    try:
        await test_server_import()
        await test_fastmcp_setup()
        await test_todo_manager()
        await test_tools_functionality()
        print("\n🎉 All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
