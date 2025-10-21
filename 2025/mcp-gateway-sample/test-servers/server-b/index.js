#!/usr/bin/env node

/**
 * Test MCP Server B - String Utilities
 * Provides string manipulation tools
 */

const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

// Server state
const serverInfo = {
  name: 'test-server-b',
  version: '1.0.0',
  description: 'String Utilities MCP Server'
};

const tools = [
  {
    name: 'uppercase',
    description: 'Convert text to uppercase',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Text to convert' }
      },
      required: ['text']
    }
  },
  {
    name: 'reverse',
    description: 'Reverse a string',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Text to reverse' }
      },
      required: ['text']
    }
  },
  {
    name: 'count_words',
    description: 'Count words in text',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Text to analyze' }
      },
      required: ['text']
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
    case 'uppercase':
      return {
        jsonrpc,
        id,
        result: {
          content: [
            {
              type: 'text',
              text: `Result: ${args.text.toUpperCase()}`
            }
          ]
        }
      };

    case 'reverse':
      return {
        jsonrpc,
        id,
        result: {
          content: [
            {
              type: 'text',
              text: `Result: ${args.text.split('').reverse().join('')}`
            }
          ]
        }
      };

    case 'count_words':
      const wordCount = args.text.trim().split(/\s+/).length;
      return {
        jsonrpc,
        id,
        result: {
          content: [
            {
              type: 'text',
              text: `Word count: ${wordCount}`
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
console.error('[Server B] String Utilities MCP Server started');
