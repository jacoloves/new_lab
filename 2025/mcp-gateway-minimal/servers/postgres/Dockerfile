FROM node:20-alpine
WORKDIR /app

# Install dependencies
RUN npm init -y && \
    npm install ws @modelcontextprotocol/sdk @modelcontextprotocol/server-postgres

# Copy wrapper script
COPY package.json ./
COPY server-wrapper.js ./

EXPOSE 8083

CMD ["node", "server-wrapper.js"]