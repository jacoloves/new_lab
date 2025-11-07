# MCP Proxy for AWS

fastMCPを使用したAWS Lambda上で動作するMCPプロキシサーバー

## セットアップ

### 前提条件
- Python 3.11+
- uv (推奨) または pip
- AWS CLI設定済み

### インストール

```bash
# uvを使用（推奨）
uv pip install -e ".[dev]"

# または pip
pip install -e ".[dev]"
```

### ローカル開発

```bash
# 環境変数設定
cp .env.example .env

# ローカルサーバー起動
python src/lambda/handler.py
```

## プロジェクト構造

```
mcp-proxy-aws/
├── src/
│   ├── lambda/          # Lambda関数コード
│   ├── config/          # 設定ファイル
│   └── utils/           # ユーティリティ
├── tests/               # テストコード
├── infrastructure/      # IaCコード（Terraform/CDK）
└── docs/               # ドキュメント
```