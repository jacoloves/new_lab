#!/bin/bash
set -e

echo "🔨 Building MCP Proxy for Lambda..."

# 依存関係を出力
echo "📦 Generating requirements.txt..."
uv pip freeze | grep -v "mcp-proxy-aws" > requirements.txt

# SAMでビルド
echo "🏗️  Building with SAM..."
sam build --use-container

echo "✅ Build completed!"