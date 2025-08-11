#! /usr/bin/env python3
"""
Todo MCP Server Runner
This script handles the import path and runs the MCP server
"""

import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Now import and run the server
from todo_mcp_server.main import main

if __name__ == "__main__":
    main()
