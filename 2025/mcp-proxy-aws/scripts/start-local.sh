#!/bin/bash
set -e

echo "🚀 Starting SAM Local API..."

# .envから環境変数を読み込み
if [ -f .env ]; then
    echo "📝 Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# ダミー認証情報を設定（念のため）
export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-test}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-test}
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-ap-northeast-1}

echo "✅ Environment variables loaded"
echo "🌐 Starting API on http://127.0.0.1:3000"
echo ""

# SAM Local起動
sam local start-api --port 3000 --warm-containers EAGER