#!/bin/bash

set -e

echo "Setting up work MCP Gateway (GitHub + Slack + Atlassian)..."
echo "Taeget: Dvelopment workflow optimization"

if [ ! -f ".env.work" ]; then
  echo ".env.work file not found. Please create it with your work credentials."
  echo "Required variables:"
  echo "- GITHUB_WORK_PAT"
  echo "- SLACK_WORK_TEAM_ID"
  echo "- SLACK_WORK_CHANNEL_IDS"
  exit 1
fi

echo "Creating work directory structure..."
mkdir -p containers/{github,slack}
mkdir -p ~/.docker/mcp
mkdir -p logs/work-mcp

echo "Applying work MCP gateway configuration..."
cp work-gateway-config.yaml ~/.docker/mcp/

echo "Setting up work secrets..."
source .env.work

# GitHub work secrets
echo "$GITHUB_WORK_PAT" | docker secret create github_work_pat - 2>/dev/null || echo "GitHub work secret already exists"

# Slack work secrets
echo "$SLACK_WORK_TEAM_ID" | docker secret create slack_work_team_id - 2>/dev/null || echo "Slack work team ID already exists"
echo "$SLACK_WORK_CHANNEL_IDS" | docker secret create slack_work_channels - 2>/dev/null || echo "Slack work channels already exists"

# work containers build
echo "Building work MCP containers..."

# GiHub work container
echo "Building GitHub work MCP server..."
cd containers/github && docker build -t mcp/github-work-server:latest . && cd ../..

# Slack work container
echo "Building Slack work MCP server..."
cd containers/slack && docker build -t mcp/github-work-server:latest . && cd ../..

# Enable server
echo "Enabling work MCP servers..."
docker mcp server enable github slack atlassian

# Starting work MCP server
echo "Starting work MCP environment..."
docker-compose -f compose.work.yml --env-file .env.work up -d

# Verifying
echo "Verifying work setup..."
sleep 15

# Check server status
echo "Work MCP Server Status:"
docker mcp server list

# Check work tool
echo "Available Work Tools:"
docker mcp tools list

# Cline/VS Code setting navigationion
echo ""
echo "Work MCP Gateway setup completed!"
echo ""
echo "Next steps for Cline/VS Code:"
echo ""
echo "1. VS Code MCP設定 (.vscode/mcp.json):"
echo '    {
     "mcp": {
       "servers": {
         "WORK_MCP": {
           "command": "docker",
           "args": ["mcp", "gateway", "run"],
           "type": "stdio"
        }
      }
    }
  }'
echo ""
echo "2. Cline設定:"
echo "   - Extension settings で MCP を有効化"
echo "   - Server path: docker mc gateway run"
echo ""
echo "3. 動作テスト用コマンド:"
echo "   'Show me my GitHub repositories'"
echo "   'List recent messages in our Slack channel'"
echo "   'Get my assigned Jira tickets'"
echo ""
echo "Mnagement commands"
echo "docker compose -f compose.work.yml logs -f  # ログ確認"
echo "docker mcp server list                      # サーバー一覧"
echo "docker mcp tools list                       # ツール一覧"
echo "docker compose -f compose.work.yml restart  # 再起動"
