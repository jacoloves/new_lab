/**
 * MCP Gateway - Router
 * Routes requests to appropriate MCP servers
 */

import { MCPRequest, MCPResponse, ServerConnection } from './types.js';

export class MCPRouter {
  private connections: Map<string, ServerConnection> = new Map();

  /**
   * Register a server connection
   */
  registerServer(connection: ServerConnection): void {
    this.connections.set(connection.name, connection);
    console.log(`[Router] Registered server: ${connection.name}`);
  }

  /**
   * Get all registered servers
   */
  getServers(): ServerConnection[] {
    return Array.from(this.connections.values());
  }

  /**
   * Get a specific server by name
   */
  getServer(name: string): ServerConnection | undefined {
    return this.connections.get(name);
  }

  /**
   * Route a request to a specific server
   */
  async routeRequest(
    serverName: string,
    request: MCPRequest
  ): Promise<MCPResponse> {
    const connection = this.connections.get(serverName);

    if (!connection) {
      return this.createErrorResponse(
        request.id,
        -32001,
        `Server '${serverName}' not found`
      );
    }

    if (!connection.connected) {
      return this.createErrorResponse(
        request.id,
        -32002,
        `Server '${serverName}' is not connected`
      );
    }

    // TODO: Implement actual request forwarding
    console.log(`[Router] Routing request to ${serverName}:`, request.method);
    
    return {
      jsonrpc: '2.0',
      id: request.id,
      result: {
        message: `Request routed to ${serverName}`,
        method: request.method
      }
    };
  }

  /**
   * Broadcast a request to all connected servers
   */
  async broadcastRequest(request: MCPRequest): Promise<MCPResponse[]> {
    const responses: MCPResponse[] = [];

    for (const [name, connection] of this.connections) {
      if (connection.connected) {
        const response = await this.routeRequest(name, request);
        responses.push(response);
      }
    }

    return responses;
  }

  /**
   * Create an error response
   */
  private createErrorResponse(
    id: string | number,
    code: number,
    message: string
  ): MCPResponse {
    return {
      jsonrpc: '2.0',
      id,
      error: {
        code,
        message
      }
    };
  }

  /**
   * Remove a server connection
   */
  unregisterServer(name: string): boolean {
    const result = this.connections.delete(name);
    if (result) {
      console.log(`[Router] Unregistered server: ${name}`);
    }
    return result;
  }
}
