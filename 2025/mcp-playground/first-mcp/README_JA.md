# Todo MCP サーバー - チーム用セットアップガイド

Model Context Protocol (MCP) を使用した Claude Desktop 向けの Docker ベース Todo リスト管理サーバーです。

## 🚀 クイックスタート

### 必要な環境
- Docker と Docker Compose がインストール済み
- Claude Desktop がインストール済み

### セットアップ（5分で完了）

1. **プロジェクトをクローン/ダウンロード**
   ```bash
   git clone <リポジトリのURL>
   cd todo-mcp-server
   ```

2. **セットアップスクリプトを実行**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Claude Desktop を設定**
   
   ファイル: `~/Library/Application Support/Claude/claude_desktop_config.json` を編集
   
   ```json
   {
     "mcpServers": {
       "todo-mcp-server": {
         "command": "docker",
         "args": [
           "exec",
           "-i", 
           "todo-mcp-server",
           "uv",
           "run",
           "python", 
           "run_server.py"
         ]
       }
     }
   }
   ```

4. **Claude Desktop を再起動**

5. **動作テスト**
   Claude Desktop を開いて試してみてください：
   ```
   「チーム会議の準備」という高優先度のタスクを追加してください
   ```

## 🛠️ 管理コマンド

```bash
# サーバーログを表示
docker compose logs -f

# サーバーを停止
docker compose down

# サーバーを再起動
docker compose restart

# コード変更後にリビルド
docker compose down
docker compose build
docker compose up -d
```

## 📊 利用可能な機能

- **add_task** - 優先度や期限付きで新しいタスクを追加
- **list_tasks** - フィルター機能付きでタスクを表示（全て/完了済み/未完了/高・中・低優先度）
- **update_task** - 既存タスクを変更
- **complete_task** / **uncomplete_task** - 完了状態の切り替え
- **delete_task** - タスクを削除
- **get_task_stats** - タスクの統計情報を表示

## 💾 データの永続化

タスクデータは `./data/todos.json` に保存され、コンテナ再起動後も保持されます。

## 🔧 トラブルシューティング

### Claude にサーバーが表示されない場合
1. コンテナが動作しているか確認: `docker compose ps`
2. ログを確認: `docker compose logs`
3. Claude Desktop 設定ファイルの構文を確認
4. Claude Desktop を完全に再起動

### 権限の問題
```bash
# データディレクトリの権限を修正
sudo chown -R $(whoami):$(whoami) ./data
chmod 755 ./data
```

### コンテナが起動しない場合
```bash
# ポートの競合をチェック
docker compose down
docker system prune -f
docker compose up -d
```

## 📋 使用例

```
# タスクの追加
「買い物リストを高優先度で追加してください」

# タスクの表示
「未完了のタスクを全て表示してください」

# タスクの完了  
「ID 1 のタスクを完了にしてください」

# 統計の確認
「タスクの統計情報を教えてください」
```

## 🔒 セキュリティに関する注意

- サーバーは非rootユーザー（mcpuser）で実行されます
- データディレクトリは適切な権限でマウントされます
- 基本動作に外部ネットワークアクセスは不要です

## 📝 開発者向け

ライブコード変更での開発の場合：

```bash
# 開発モード（ボリュームマウント付き）
docker compose -f compose.dev.yml up -d
```

## 💡 使い方のコツ

### タスク追加の例
```
「プロジェクト企画書の作成」を高優先度で、期限を 2024-12-25 15:00 で追加してください
```

### フィルター表示の例
```
高優先度のタスクだけ表示してください
```

### 一括操作の例
```
完了済みのタスクを全て表示してください
```

## 🤝 サポート

問題が発生した場合：
1. 上記のトラブルシューティングを確認
2. コンテナログを確認: `docker compose logs`
3. Docker と Claude Desktop が最新版であることを確認
4. 必要に応じて開発チームに相談

## 📖 関連ドキュメント

- [Model Context Protocol 公式ドキュメント](https://modelcontextprotocol.io/)
- [Claude Desktop ユーザーガイド](https://claude.ai/help)

