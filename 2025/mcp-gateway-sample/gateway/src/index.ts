/**
 * MCP Gateway - Main Entry Point
 */

import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { MCPGateway } from './gateway.js';
import { GatewayConfig } from './types.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function main() {
  console.log('🚀 MCP Gateway Starting...\n');

  // Load configuration
  const configPath = join(__dirname, '../config/servers.json');
  console.log(`📄 Loading configuration from: ${configPath}`);
  
  let config: GatewayConfig;
  try {
    const configContent = readFileSync(configPath, 'utf-8');
    config = JSON.parse(configContent);
    console.log(`✅ Configuration loaded: ${config.servers.length} servers configured\n`);
  } catch (error) {
    console.error('❌ Failed to load configuration:', error);
    process.exit(1);
  }

  // Create gateway instance
  const gateway = new MCPGateway();

  // Setup graceful shutdown
  const shutdown = async () => {
    console.log('\n\n🛑 Received shutdown signal...');
    await gateway.shutdown();
    process.exit(0);
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);

  // Connect to all servers
  try {
    await gateway.connectAll(config.servers);
  } catch (error) {
    console.error('❌ Failed to initialize gateway:', error);
    process.exit(1);
  }

  // Display server statuses
  console.log('\n📊 Server Status:');
  console.log('─'.repeat(60));
  const statuses = gateway.getServerStatuses();
  for (const status of statuses) {
    const statusIcon = status.connected ? '✅' : '❌';
    const errorMsg = status.lastError ? ` (${status.lastError})` : '';
    console.log(`${statusIcon} ${status.name}: ${status.config.transport}${errorMsg}`);
  }
  console.log('─'.repeat(60));

  // Example: Send a test request
  console.log('\n🧪 Testing request routing...');
  
  if (statuses.length > 0 && statuses[0].connected) {
    const testRequest = {
      jsonrpc: '2.0' as const,
      id: 1,
      method: 'tools/list',
      params: {}
    };

    console.log(`\n📤 Sending test request to: ${statuses[0].name}`);
    const response = await gateway.sendRequest(statuses[0].name, testRequest);
    console.log('📥 Response:', JSON.stringify(response, null, 2));
  }

  // Keep the process running
  console.log('\n✨ Gateway is running. Press Ctrl+C to shutdown.\n');
  
  // Display help
  console.log('💡 Gateway Commands:');
  console.log('   - Press Ctrl+C to shutdown');
  console.log('   - Check logs above for server statuses\n');
}

// Run the gateway
main().catch((error) => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});
