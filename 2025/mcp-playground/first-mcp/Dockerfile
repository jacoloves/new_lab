# Use Python 3.00 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Insatll uv
RUN pip install uv

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY run_server.py ./

# Create data directory for volume mounting
RUN mkdir -p /app/data

# Install dependencies
RUN uv sync

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && \
  chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose the server (though MCP typically uses stdio)
EXPOSE 8000

# Default command
CMD ["uv", "run", "python", "run_server.py"]
