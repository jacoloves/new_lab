/**
 * MCP Gateway - Type Definitions
 */

export interface MCPServerConfig {
  name: string;
  transport: 'stdio' | 'http' | 'sse';
  command?: string;
  args?: string[];
  env?: Record<string, string>;
  url?: string;
}

export interface GatewayConfig {
  servers: MCPServerConfig[];
  port?: number;
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
}

export interface MCPRequest {
  jsonrpc: '2.0';
  id: string | number;
  method: string;
  params?: any;
}

export interface MCPResponse {
  jsonrpc: '2.0';
  id: string | number;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

export interface MCPNotification {
  jsonrpc: '2.0';
  method: string;
  params?: any;
}

export interface ServerConnection {
  name: string;
  config: MCPServerConfig;
  connected: boolean;
  lastError?: string;
}
