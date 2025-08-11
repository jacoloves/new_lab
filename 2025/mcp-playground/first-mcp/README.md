# Todo MCP Server - Team Setup Guide

A Docker-based Todo list management server for Claude Desktop using the Model Context Protocol (MCP).

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Claude Desktop installed

### Setup (5 minutes)

1. **Clone/download this project**
   ```bash
   git clone <repository-url>
   cd todo-mcp-server
   ```

2. **Run setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure Claude Desktop**
   
   Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`
   
   ```json
   {
     "mcpServers": {
       "todo-mcp-server": {
         "command": "docker",
         "args": [
           "exec",
           "-i", 
           "todo-mcp-server",
           "uv",
           "run",
           "python", 
           "run_server.py"
         ]
       }
     }
   }
   ```

4. **Restart Claude Desktop**

5. **Test it!**
   Open Claude Desktop and try:
   ```
   Add a high-priority task called "Team Meeting Prep"
   ```

## 🛠️ Management Commands

```bash
# View server logs
docker compose logs -f

# Stop the server
docker compose down

# Restart the server
docker compose restart

# Rebuild after code changes
docker compose down
docker compose build
docker compose up -d
```

## 📊 Available Tools

- **add_task** - Add new tasks with priority and due dates
- **list_tasks** - View tasks with filtering (all/completed/pending/high/medium/low)
- **update_task** - Modify existing tasks
- **complete_task** / **uncomplete_task** - Mark completion status
- **delete_task** - Remove tasks
- **get_task_stats** - View task statistics

## 💾 Data Persistence

Task data is saved in `./data/todos.json` and persists between container restarts.

## 🔧 Troubleshooting

### Server not showing in Claude
1. Check container is running: `docker-compose ps`
2. Check logs: `docker-compose logs`
3. Verify Claude Desktop config file syntax
4. Restart Claude Desktop completely

### Permission issues
```bash
# Fix data directory permissions
sudo chown -R $(whoami):$(whoami) ./data
chmod 755 ./data
```

### Container won't start
```bash
# Check for port conflicts
docker compose down
docker system prune -f
docker compose up -d
```

## 📋 Example Usage

```
# Add tasks
"Add a task 'Buy groceries' with high priority"

# View tasks
"Show me all pending tasks"

# Complete tasks  
"Mark task ID 1 as completed"

# Get overview
"Show me task statistics"
```

## 🔒 Security Notes

- Server runs as non-root user (mcpuser)
- Data directory is mounted with appropriate permissions
- No external network access required for basic operation

## 📝 Development

For development with live code changes:

```bash
# Development mode with volume mounting
docker compose -f compose.dev.yml up -d
```

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review container logs: `docker compose logs`
3. Ensure Docker and Claude Desktop are up to date
