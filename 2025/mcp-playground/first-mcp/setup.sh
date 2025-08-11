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
docker compose build

echo "🚀 Stating Todo MCP Server..."
docker compose up -d

# Wait for container to be ready
echo "⏳ Waiting for server to be ready..."
sleep 5

# Check if container is running
if docker compose ps | gerp -q "Up"; then
	echo "✅ Todo MCP Server is running!"
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
	echo "2. Restart Claud Desktop"
	echo "3. Test with: 'Add a task called \"Test Task\"'"
	echo ""
	echo "📊 Management commands:"
	echo "   View logs:    docker compose logs -f"
	echo "   Stop server:  docker compose down"
	echo "   Restart:      docker compose restart"
	echo ""
else
	echo "❌ Failed to start the server. Check logs with:"
	echo "   docker compose logs"
	exit 1
fi
