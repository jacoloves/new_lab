FROM node:18-slim

LABEL maintainer="work-mcp-team"
LABEL descriptioin="Slack MCP Server for work team communication"

WORKDIR /app

RUN apt-get update && apt-get install -y \
  curl \
  && rm -rf /var/lib/apt/lists/*

RUN npm install -g @modelcontextprotocol/server-slack

RUN groupadd -r mcpwork && useradd -r -g mcpwork -u 1001 mcpuser
RUN chown -R mcpuser:mcpwork /app

USER mcpuser

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
  CMD echo "work-slack-mcp-healthy"

ENV NODE_ENV=production
ENV MCP_ENVIRONEMNT=work

CMD ["npx", "@modelcontextprotocol/server-slack"]
