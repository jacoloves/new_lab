FROM node:20-alipine
WORKDIR /app

# Install dependencies
RUN npm init -y && \
    npm install ws @modelcontextprotocol/sdk @modelcontextprotocol/server-filesystem

# Copy wrapper script
COPY package.json ./
COPY server-wrapper.js ./

# Create workspace directory
RUN mkdir -p /workspace

EXPOSE 8081

CMD ["node", "server-wrapper.js"]
