import { WebSocketServer } from 'ws';
import { spawn } from 'child_process';
import { createServer } from 'http';

const serverType = process.env.SERVER_TYPE || 'filesystem';
const port = process.env.PORT || 8080;

console.log(`Starting MCP ${serverType} server on port ${port}...`);

// Create HTTP server
const httpServer = createServer((req, res) => {
    if (req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'healthy', serverType }));
    } else {
        res.writeHead(404);
        res.end();
    }
});

// Create WebSocket server
const wss = new WebSocketServer({ server: httpServer });

// connection management
const connections = new Map();

wss.on('connection', (ws, req) => {
    const connectionId = Math.random().toString(36).substring(7)
    console.log(`New connection: ${connectionId} from ${req.socket.remoteAddress}`);

    // Enable MCP server process
    const mcpCommand = getMcpCommand(serverType);
    const mcpArgs = getMcpArgs(serverType);

    console.log(`Spawning MCP process: ${mcpCommand} ${mcpArgs.join(' ')}`);
    
    const mcpProcess = spawn(mcpCommand, mcpArgs, {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
            ...process.env,
            // Add any necessary environment variables here
            ...getMcpEnv(serverType)    
        }
    }); 

    connections.set(connectionId, { ws, mcpProcess });

    // WebSocket -> MCP Server (stdin)
    ws.on('message', (data) => {
        try {
            const message = data.toString();
            console.log(`[${connectionId}] Client -> MCP:`, message.substring(0, 100));
            mcpProcess.stdin.write(message + '\n');
        } catch (error) {
            console.error(`[${connectionId}] Error forwarding to MCP:`, error);
        }
    });
    
    // MCP Server (stdout) -> WebSocket
    mcpProcess.stdout.on('data', (data) => {
       try {
        const message = data.toString().trim();
        console.log(`[${connectionId}] MCP -> Client:`, message.substring(0, 100));
        ws.send(message) ;
       } catch (error)  {
        console.error(`[${connectionId}] Error sending to client:`, error);
        
       }
    });
    
    // MCP Server (stderr) -> Log
    mcpProcess.stderr.on('data', (data) => {
        console.error(`[${connectionId}] MCP stderr:`, data.toString());
    });
    
    // Error handling
    mcpProcess.on('error', (error) => {
        console.error(`[${connectionId}] MCP process error:`, error);
        ws.close(1011, 'MCP process error');
    });
    
    mcpProcess.on('exit', (code, signal) => {
        console.log(`[${connectionId}] MCP process exited with code ${code}, signal ${signal}`);
        if (ws.readyState === ws.OPEN) {
            ws.close(1011, 'MCP server terminated');
        }
    });
    
    // Cleanup on WebSocket close
    ws.on('close', () => {
        console.log(`${connectionId} Connection closed`);
        if (mcpProcess && !mcpProcess.killed) {
            mcpProcess.kill();
        }
        connections.delete(connectionId);
    });

    ws.on('error', (error) => {
        console.error(`[${connectionId}] WebSocket error:`, error);
    });
});
        
    
// Start HTTP server
httpServer.listen(port, '0.0.0.0', () => {
    console.log(`MCP ${serverType} server listening on port ${port}`);
    console.log(`Health check: http://localhost:${port}/health`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, closing connections...');
    connections.forEach(({ ws, mcpProcess }) => {
        ws.close();
        mcpProcess.kill();
    });
    httpServer.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

// Get MCP command based on server type
function getMcpCommand(type) {
    // For simplicity, we assume 'npx' is used to run MCP servers
    return 'npx';
}

// Get MCP arguments based on server type
function getMcpArgs(type) {
    switch (type) {
        case 'filesystem':
            return ['-y', '@modelcontextprotocol/server-filesystem'];
        case 'github':
            return ['-y', '@modelcontextprotocol/server-github'];
        case 'postgres':
            return ['-y', '@modelcontextprotocol/server-postgres'];
        default:
            throw new Error(`Unknown server type: ${type}`);
    }
}

// Get MCP environment variables based on server type
function getMcpEnv(type) {
    const env = {};

    switch (type) {
        case 'filesystem':
            if (process.env.ALLOWED_DIRECTORIES) {
                env.ALLOWED_DIRECTORIES = process.env.ALLOWED_DIRECTORIES;
            }
            break;
        case 'github':
            if (process.env.GITHUB_TOKEN) {
                env.GITHUB_TOKEN = process.env.GITHUB_TOKEN;
            }
            break;
        case 'postgres':
            if (process.env.POSTGRES_CONNECTION_STRING) {
                env.POSTGRES_CONNECTION_STRING = process.env.POSTGRES_CONNECTION_STRING;
            }
            break;
    }

    return env;
}