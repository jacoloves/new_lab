#!/usr/bin/env node

/**
 * Test MCP Server A - Calculator
 * Provides basic calculator tools
 */

const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

// Server state
const serverInfo = {
  name: 'test-server-a',
  version: '1.0.0',
  description: 'Calculator MCP Server'
};

const tools = [
  {
    name: 'add',
    description: 'Add two numbers',
    inputSchema: {
      type: 'object',
      properties: {
        a: { type: 'number', description: 'First number' },
        b: { type: 'number', description: 'Second number' }
      },
      required: ['a', 'b']
    }
  },
  {
    name: 'multiply',
    description: 'Multiply two numbers',
    inputSchema: {
      type: 'object',
      properties: {
        a: { type: 'number', description: 'First number' },
        b: { type: 'number', description: 'Second number' }
      },
      required: ['a', 'b']
    }
  }
];

// Handle incoming messages
rl.on('line', (line) => {
  try {
    const request = JSON.parse(line);
    const response = handleRequest(request);
    console.log(JSON.stringify(response));
  } catch (error) {
    console.error('Error processing request:', error);
  }
});

function handleRequest(request) {
  const { jsonrpc, id, method, params } = request;

  switch (method) {
    case 'initialize':
      return {
        jsonrpc,
        id,
        result: {
          protocolVersion: '2024-11-05',
          capabilities: {
            tools: {}
          },
          serverInfo
        }
      };

    case 'tools/list':
      return {
        jsonrpc,
        id,
        result: {
          tools
        }
      };

    case 'tools/call':
      return handleToolCall(jsonrpc, id, params);

    default:
      return {
        jsonrpc,
        id,
        error: {
          code: -32601,
          message: `Method not found: ${method}`
        }
      };
  }
}

function handleToolCall(jsonrpc, id, params) {
  const { name, arguments: args } = params;

  switch (name) {
    case 'add':
      return {
        jsonrpc,
        id,
        result: {
          content: [
            {
              type: 'text',
              text: `Result: ${args.a + args.b}`
            }
          ]
        }
      };

    case 'multiply':
      return {
        jsonrpc,
        id,
        result: {
          content: [
            {
              type: 'text',
              text: `Result: ${args.a * args.b}`
            }
          ]
        }
      };

    default:
      return {
        jsonrpc,
        id,
        error: {
          code: -32602,
          message: `Unknown tool: ${name}`
        }
      };
  }
}

// Startup message
console.error('[Server A] Calculator MCP Server started');
