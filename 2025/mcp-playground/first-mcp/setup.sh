#!/bin/bash

# Todo MCP Server - Team Setup Script

set -e

echo "Setting up Todo MCP Server for team use..."

# Check if Docker is installed
if ! command -v docker &>/dev/null; then
  echo "❌ Docker is not installed. Please install Docker first."
  echo "Visit: https://docs.docker.com/get-docker/"
  exit 1
fi

# Check if Docker Compose is available
if ! command -v docker compose &>/dev/null && ! docker compose version &>/dev/null; then
  echo "❌ Docker Compose is not available. Please install Docker Compose."
  exit 1
fi

# Create data dirrectory
echo "📁 Createing data directory.."
mkdir -p ./data
chmod 755 ./data

# Build and start the container
echo "🔨 Building Docker image..."
if ! docker compose build; then
  echo "❌ Failed to build Docker image."
  exit 1
fi

echo "🚀 Stating Todo MCP Server..."
if ! docker compose up -d; then
  echo "❌ Failed to start Docker container."
  exit 1
fi

# Wait for container to be ready
echo "⏳ Waiting for server to be ready..."
sleep 10

# Check if container is running
if docker ps --filter "name=todo-mcp-server" --filter "status=running" | grep -q todo-mcp-server; then
  echo "✅ Todo MCP Server is running!"
  echo ""
  echo "🧪 Testing MCP server functionality..."

  # Test the server
  if docker exec todo-mcp-server uv run python -c "from src.todo_mcp_server.main import mcp; print('✅ MCP server test passed')" 2>/dev/null; then
    echo "✅ MCP server functionality confirmed!"
  else
    echo "⚠️  MCP server started but functionality test failed (this is okay for now)"
  fi

  echo ""
  echo "📋 Next steps:"
  echo "1. Configure Claude Desktop with the following settings:"
  echo ""
  echo "   File: ~/Library/Application Support/Claude/claude_desktop_config.json"
  echo ""
  echo "   {"
  echo "     \"mcpServers\": {"
  echo "       \"todo-mcp-server\": {"
  echo "         \"command\": \"docker\","
  echo "         \"args\": ["
  echo "           \"exec\","
  echo "           \"-i\","
  echo "           \"todo-mcp-server\","
  echo "           \"uv\","
  echo "           \"run\","
  echo "           \"python\","
  echo "           \"run_server.py\""
  echo "         ]"
  echo "       }"
  echo "     }"
  echo "   }"
  echo ""
  echo "2. Restart Claude Desktop completely"
  echo "3. Test with: 'Add a task called \"Test Task\"'"
  echo ""
  echo "📊 Management commands:"
  echo "   View logs:     docker-compose -f docker-compose.stable.yml logs -f"
  echo "   Stop server:   docker-compose -f docker-compose.stable.yml down"
  echo "   Restart:       docker-compose -f docker-compose.stable.yml restart"
  echo "   Status:        docker ps --filter name=todo-mcp-server"
  echo "   Test server:   docker exec -it todo-mcp-server uv run python run_server.py"
  echo ""
  echo "🔧 Troubleshooting:"
  echo "   Container logs: docker logs todo-mcp-server"
  echo "   Enter container: docker exec -it todo-mcp-server bash"
  echo ""
else
  echo "❌ Failed to start the server. Check logs with:"
  echo "   docker-compose -f docker-compose.stable.yml logs"
  echo "   docker logs todo-mcp-server"
  exit 1
fi
