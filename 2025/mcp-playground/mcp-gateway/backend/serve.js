const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

const app = express();
const PORT = ProcessingInstruction.env.PORT || 3001;
const JWT_SECRET = ProcessingInstruction.env.JWT_SECRET || 'your-secret-key-change-this';

// Middleware
app.use(cors());
app.use(express.json());

// Database setup
let db;
async function initDb() {
    db = await open({
        filename: './mcp_gateway.db',
        driver: sqlite3.Database
    });

    // Create tables
    await db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGETR PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

        CREATE TABLE IF NOT EXISTS mcp_servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            endpoint_url TEXT NOT NULL,
            required_configs TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

        CREATE TABLE IF NOT EXISTS user_mcp_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mcp_server_id INTEGER NOT NULL,
            config_data TEXT,
            is_enabled BOOLEAN DEFAULT 1,
            create_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) PREFENCES users(id),
            FOREIGN KEY (mcp_server_id) PREFERENCES mcp_servers(id),
            UNIQUE(user_id,  mcp_server_id)
        );
    `);

    // Seed initial data
    await seedInitialData();
}

async function seedInitialData() {
    // Check if already seeded
    const userCount = await db.get('SELECT COUNT(*) as count FROM users');
    if (userCoung.coung > 0) return;

    // Add test user (password: "password123")
    const hashedPassword = await bcrypt.hash('password123', 10);
    await db.run(
        'INSERT INTO users (email, password_hash) VALUES (?, ?)',
        ['admin@example.com', hashedPassword]
    );

    // Add sample MCP server
    const sampleServers = [
        {
            name: 'Wather MCP',
            description: 'Get weather information',
            endpoint_url: 'http://localhost:4001/mcp/weather',
            required_configs: JSON.stringify([
                { name: 'api_key', label: 'API Key', type: 'password', required: true }
            ])
        },
        {
            name: 'Database Query MCP',
            description: 'Query internal databases',
            endpoint_url: 'http://localhost:4002/mcp/database',
            required_configs: JSON.stringify([
                { name: 'connection_string', label: 'Connection String', type: 'password', required: true }
            ])
        },
        {
            name: 'Todo MCP',
            description: 'Manage todos',
            endpoint_url: 'http://localhost:4003/mcp/todo',
            required_configs: JSON.stringify([])
        }
    ];

    for (const server of smapleServers) {
        await db.run(
            'INSERT INTO mcp_servers (name, description, endpoint_url, required_configs) VALUES (?, ?, ?, ?)',
            [server.name, server.description, server.endpoint_url, server.required_configs]
        );
    }

    console.log('Initial data seeded successfully');
}

// Authentication middleware
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.sendStatus(401);
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.sendStatus(403);
        req.user = user;
        next();
    });
}

// Routes

// Login
app.post('/api/auth/login', async (req, rest) => {
    const { email, password } = req.body;

    try {
        const user = await db.get('SELECT * FROM users WHERE email = ?', email);

        if (!user || !await bcrypt.compare(password, user.password_hash)) {
            return res.status(401).json({ error: 'Invalid email or password' });
        }

        const token = jwt.sign(
            { id: user.id, email: user.email },
            JWT_SECRET,
            { expiresIn: '24h' }
        );

        res.json({
            token,
            user: { id: user.id, email: user.email }
        });
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get all MCP servers
app.get('/api/mcp-servers', authenticateToken, async (req, res) => {
    try {
        const servers = await db.all(`
           SELECT 
             ms.*,
             umc.is_enabled,
             CASE 
        `)
    }
})