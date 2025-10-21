/**
 * MCP Gateway - Core Logic
 */

import { spawn, ChildProcess } from 'child_process';
import { MCPServerConfig, ServerConnection, MCPRequest, MCPResponse } from './types.js';
import { MCPRouter } from './router.js';

export class MCPGateway {
  private router: MCPRouter;
  private processes: Map<string, ChildProcess> = new Map();

  constructor() {
    this.router = new MCPRouter();
  }

  /**
   * Connect to a stdio-based MCP server
   */
  async connectStdioServer(config: MCPServerConfig): Promise<void> {
    if (!config.command) {
      throw new Error(`Command is required for stdio transport: ${config.name}`);
    }

    console.log(`[Gateway] Connecting to stdio server: ${config.name}`);

    try {
      const childProcess = spawn(config.command, config.args || [], {
        env: { ...process.env, ...config.env },
        stdio: ['pipe', 'pipe', 'pipe']
      });

      this.processes.set(config.name, childProcess);

      // Handle stdout
      childProcess.stdout?.on('data', (data) => {
        console.log(`[${config.name}] stdout:`, data.toString().trim());
      });

      // Handle stderr
      childProcess.stderr?.on('data', (data) => {
        console.error(`[${config.name}] stderr:`, data.toString().trim());
      });

      // Handle process exit
      childProcess.on('exit', (code) => {
        console.log(`[${config.name}] Process exited with code ${code}`);
        this.processes.delete(config.name);
        
        const connection = this.router.getServer(config.name);
        if (connection) {
          connection.connected = false;
        }
      });

      // Handle process error
      childProcess.on('error', (error) => {
        console.error(`[${config.name}] Process error:`, error);
        
        const connection = this.router.getServer(config.name);
        if (connection) {
          connection.connected = false;
          connection.lastError = error.message;
        }
      });

      // Register with router
      const connection: ServerConnection = {
        name: config.name,
        config,
        connected: true
      };

      this.router.registerServer(connection);

      console.log(`[Gateway] ✅ Connected to ${config.name}`);
    } catch (error) {
      console.error(`[Gateway] Failed to connect to ${config.name}:`, error);
      throw error;
    }
  }

  /**
   * Connect to an HTTP-based MCP server
   */
  async connectHttpServer(config: MCPServerConfig): Promise<void> {
    if (!config.url) {
      throw new Error(`URL is required for HTTP transport: ${config.name}`);
    }

    console.log(`[Gateway] Connecting to HTTP server: ${config.name} (${config.url})`);

    // TODO: Implement HTTP connection logic
    const connection: ServerConnection = {
      name: config.name,
      config,
      connected: true
    };

    this.router.registerServer(connection);
    console.log(`[Gateway] ✅ Connected to ${config.name}`);
  }

  /**
   * Connect to all configured servers
   */
  async connectAll(configs: MCPServerConfig[]): Promise<void> {
    console.log(`[Gateway] Connecting to ${configs.length} servers...`);

    for (const config of configs) {
      try {
        switch (config.transport) {
          case 'stdio':
            await this.connectStdioServer(config);
            break;
          case 'http':
            await this.connectHttpServer(config);
            break;
          case 'sse':
            console.warn(`[Gateway] SSE transport not yet implemented for ${config.name}`);
            break;
          default:
            console.error(`[Gateway] Unknown transport type for ${config.name}: ${config.transport}`);
        }
      } catch (error) {
        console.error(`[Gateway] Failed to connect to ${config.name}:`, error);
      }
    }

    console.log(`[Gateway] ✅ Gateway initialization complete`);
  }

  /**
   * Send a request to a specific server
   */
  async sendRequest(serverName: string, request: MCPRequest): Promise<MCPResponse> {
    return this.router.routeRequest(serverName, request);
  }

  /**
   * Broadcast a request to all servers
   */
  async broadcastRequest(request: MCPRequest): Promise<MCPResponse[]> {
    return this.router.broadcastRequest(request);
  }

  /**
   * Get all server statuses
   */
  getServerStatuses(): ServerConnection[] {
    return this.router.getServers();
  }

  /**
   * Disconnect from a specific server
   */
  async disconnect(serverName: string): Promise<void> {
    const childProcess = this.processes.get(serverName);
    if (childProcess) {
      childProcess.kill();
      this.processes.delete(serverName);
    }

    this.router.unregisterServer(serverName);
    console.log(`[Gateway] Disconnected from ${serverName}`);
  }

  /**
   * Disconnect from all servers and cleanup
   */
  async shutdown(): Promise<void> {
    console.log('[Gateway] Shutting down...');

    for (const [name, childProcess] of this.processes) {
      console.log(`[Gateway] Terminating ${name}...`);
      childProcess.kill();
    }

    this.processes.clear();
    console.log('[Gateway] ✅ Shutdown complete');
  }
}
