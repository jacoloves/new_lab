# MCP Gateway

MCPサーバーを集約して、単一のエンドポイントから複数のMCPサーバーにアクセスできるゲートウェイです。

## 🎯 目的

複数のMCPサーバーを接続する際、設定ファイルが長くなる問題を解決します。
MCP Gatewayを使用することで、設定ファイルを1〜3行程度に収めることができます。

## 📁 プロジェクト構造

```
mcp-gateway-sample/
├── gateway/              # Gatewayアプリケーション
│   ├── src/
│   │   ├── index.ts      # エントリーポイント
│   │   ├── gateway.ts    # コアロジック
│   │   ├── router.ts     # ルーティング
│   │   └── types.ts      # 型定義
│   ├── config/
│   │   └── servers.json  # MCPサーバー設定
│   └── package.json
│
└── test-servers/         # テスト用MCPサーバー
    ├── server-a/         # 計算機能サーバー
    └── server-b/         # 文字列操作サーバー
```

## 🚀 クイックスタート

### 1. 依存関係のインストール（既に完了）

```bash
cd gateway
npm install
```

### 2. Gatewayの起動

```bash
cd gateway
npm run dev
```

### 3. 実行結果の確認

以下のような出力が表示されます：

```
🚀 MCP Gateway Starting...

📄 Loading configuration from: /path/to/config/servers.json
✅ Configuration loaded: 2 servers configured

[Gateway] Connecting to 2 servers...
[Gateway] Connecting to stdio server: test-server-a
[test-server-a] Calculator MCP Server started
[Gateway] ✅ Connected to test-server-a
[Gateway] Connecting to stdio server: test-server-b
[test-server-b] String Utilities MCP Server started
[Gateway] ✅ Connected to test-server-b
[Gateway] ✅ Gateway initialization complete

📊 Server Status:
────────────────────────────────────────────────────────────
✅ test-server-a: stdio
✅ test-server-b: stdio
────────────────────────────────────────────────────────────

✨ Gateway is running. Press Ctrl+C to shutdown.
```

## ⚙️ 設定ファイル

`gateway/config/servers.json` でMCPサーバーを設定します：

```json
{
  "servers": [
    {
      "name": "test-server-a",
      "transport": "stdio",
      "command": "node",
      "args": ["../test-servers/server-a/index.js"],
      "env": {}
    },
    {
      "name": "test-server-b",
      "transport": "stdio",
      "command": "node",
      "args": ["../test-servers/server-b/index.js"],
      "env": {}
    }
  ],
  "port": 3000,
  "logLevel": "info"
}
```

## 🧪 テストサーバー

### Server A (Calculator)
- `add`: 2つの数値を足し算
- `multiply`: 2つの数値を掛け算

### Server B (String Utilities)
- `uppercase`: 文字列を大文字に変換
- `reverse`: 文字列を反転
- `count_words`: 単語数をカウント

## 📝 次のステップ

- [ ] 実際のMCP通信プロトコルの実装
- [ ] HTTPトランスポートの実装
- [ ] SSEトランスポートの実装
- [ ] WebSocketサポート
- [ ] 認証・認可機能
- [ ] ロギング強化
- [ ] メトリクス収集

## 🔧 開発コマンド

```bash
# 開発モード（ホットリロード）
npm run dev

# ビルド
npm run build

# 本番実行
npm run start
```

## 📖 参考資料

- [Docker MCP Gateway](https://docs.docker.com/ai/mcp-catalog-and-toolkit/mcp-gateway/)
- [Qiita記事](https://qiita.com/moritalous/items/8789a37b7db451cc1dba)

## 🎯 アーキテクチャ

```
                          ─ ─ ─> MCPサーバーA 
                          │
AI Agent -> MCP Gateway ─ ├ ─ ─> MCPサーバーB
                          │
                          ─ ─ ─> MCPサーバーC
```

## 📄 ライセンス

ISC
