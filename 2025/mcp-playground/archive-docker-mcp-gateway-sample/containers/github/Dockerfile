FROM node:18-slim

LABEL maintainer="work-mcp-team"
LABEL description="GitHub MCP Server for work development workflow"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @modelcontextprotocol/server-github

RUN groupadd -r mcpwork && useradd -r -g mcpwork -u 1001 mcpuser
RUN chown -R mcpuser:mcpwork /app

USER mcpuser

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
  CMD echo "work-github-mcp-healthy"

ENV NODE_ENV=production
ENV MCP_ENVIRONMENT=work

CMD ["npx", "@modelcontextprotocol/server-github"]
