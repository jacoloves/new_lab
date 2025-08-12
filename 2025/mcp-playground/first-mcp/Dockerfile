# Use Python 3.00 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Insatll uv adn basic tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY run_server.py ./

# Create data directory for volume mounting
RUN mkdir -p /app/data /root/.todo_mcp

# Install dependencies
RUN uv sync

# Expose the server (though MCP typically uses stdio)
RUN echo '#!/bin/bash\necho "🚀 Container started and ready"\necho "💡 To run MCP: docker exec -it todo-mcp-server uv run python run_server.py"\nwhile true; do\n  sleep 3600\n  echo "📋 Container still running at $(date)"\ndone' > /app/keep_alive.sh \
    && chmod +x /app/keep_alive.sh

# Default command
CMD ["/app/keep_alive.sh"]

