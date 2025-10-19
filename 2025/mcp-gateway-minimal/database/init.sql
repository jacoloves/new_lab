-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- MCP Servers table
CREATE TABLE IF NOT EXISTS mcp_servers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    docker_image VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    env_schema JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User MCP Configs table
CREATE TABLE IF NOT EXISTS user_mcp_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    server_id UUID REFERENCES mcp_servers(id) ON DELETE CASCADE,
    config JSONB DEFAULT '{}',
    is_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, server_id)
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_user_configs_user_id ON user_mcp_configs(user_id);
CREATE INDEX idx_user_configs_server_id ON user_mcp_configs(server_id);

-- Insert default MCP servers
INSERT INTO mcp_servers (name, type, description, docker_image, port, env_schema) VALUES
(
    'Filesystem',
    'filesystem',
    'Access and manage local files and directories',
    'mcp-filesystem:latest',
    8081,
    '{
        "ALLOWED_DIRECTORIES": {
            "type": "string",
            "description": "Comma-separated list of allowed directory paths",
            "required": true,
            "example": "/home/user/documents,/home/user/projects"
        }
    }'::jsonb
),
(
    'GitHub',
    'github',
    'Interact with GitHub repositories and APIs',
    'mcp-github:latest',
    8082,
    '{
        "GITHUB_TOKEN": {
            "type": "string",
            "description": "GitHub Personal Access Token",
            "required": true,
            "secret": true
        }
    }'::jsonb
),
(
    'PostgreSQL',
    'postgres',
    'Query and manage PostgreSQL databases',
    'mcp-postgres:latest',
    8083,
    '{
        "POSTGRES_CONNECTION_STRING": {
            "type": "string",
            "description": "PostgreSQL connection string",
            "required": true,
            "example": "postgresql://user:password@host:5432/dbname",
            "secret": true
        }
    }'::jsonb
);

-- Insert test user (password: `password123` - bcrypt hash)
INSERT INTO users (email, password_hash) VALUES
('test@company.com', '$2a$10$rXXXiIXtUrhMFpcMVgpAH.Kk0tHSCaKpPXzPdpWzKrPLmQzFc3PZ2');

-- Grant test user access to filesystem server (as example)
INSERT INTO user_mcp_configs (user_id, server_id, config, is_enabled)
SELECT
    u.id,
    s.id,
    '{"ALLOWED_DIRECTORIES": "/workspace"}'::jsonb,
    true
FROM users u, mcp_servers s
WHERE u.email = 'test@company.com' AND s.type = 'filesystem';