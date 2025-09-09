# Serena MCP リモートホストアーキテクチャプラン

## 1. 概要

このアーキテクチャは、AWS EC2インスタンス上にDocker Composeを利用して **Serena MCP** と **Nginx (リバースプロキシ)** の2つのコンテナを起動し、ローカルから安全に接続することを目的とします。

- **セキュリティ**: NginxでSSL/TLS通信の暗号化とBasic認証によるアクセス制御を行います。
- **ロギング**: DockerコンテナのログをAWS CloudWatch Logsに集約し、監視と監査を容易にします。

### 構成図

```
[ローカルマシン (Cline)]
       |
       | (インターネット経由 - HTTPS / Basic認証)
       v
[AWS EC2 インスタンス]
+--------------------------------------------------+
|  [Nginx コンテナ (ポート 443)]                   |
|   - SSL/TLS終端                                  |
|   - Basic認証                                    |
|   - アクセスログ -> CloudWatch Logs              |
|                  |                               |
|                  | (HTTP)                        |
|                  v                               |
|  [Serena MCP コンテナ (内部ポート)]              |
|   - ログ -> CloudWatch Logs                      |
|                                                  |
+--------------------------------------------------+
|  [Docker Volume]                                 |
|   - Serena設定/プロジェクトデータ                |
|   - Nginx設定 / SSL証明書                        |
+--------------------------------------------------+
```

---

## 2. 各コンポーネントの具体的な設定

### A. Docker環境 (`docker-compose.yml`)

EC2インスタンス上で以下の `docker-compose.yml` を使用して、2つのサービスを管理します。

```yaml
version: '3.8'

services:
  serena:
    image: ghcr.io/oraios/serena:latest
    container_name: serena_mcp
    restart: always
    command: serena start-mcp-server --transport sse --host 0.0.0.0 --port 9121
    volumes:
      - serena_data:/root/.serena  # 設定ファイルの永続化
      - /path/to/your/projects:/workspaces/projects # ローカルのプロジェクトディレクトリをマウント
    logging:
      driver: "awslogs"
      options:
        awslogs-group: "serena-mcp-logs"
        awslogs-region: "ap-northeast-1" # ご利用のリージョンに変更してください
        awslogs-stream-prefix: "serena"

  nginx:
    image: nginx:latest
    container_name: nginx_proxy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/auth:/etc/nginx/auth:ro
      - /path/to/ssl_certs:/etc/ssl/certs:ro # SSL証明書のパス
    depends_on:
      - serena
    logging:
      driver: "awslogs"
      options:
        awslogs-group: "serena-mcp-logs"
        awslogs-region: "ap-northeast-1" # ご利用のリージョンに変更してください
        awslogs-stream-prefix: "nginx"

volumes:
  serena_data:
```

### B. Serena MCPコンテナ

- **イメージ**: 公式のDockerイメージ `ghcr.io/oraios/serena:latest` を使用します。
- **コマンド**: リモートから接続できるよう、`--transport sse --host 0.0.0.0 --port 9121` オプション付きでサーバーを起動します。
- **ボリューム**: Serenaの設定ファイル (`/root/.serena`) と、作業対象のプロジェクトディレクトリを永続化し、コンテナが再起動してもデータが消えないようにします。

### C. Nginxコンテナ (リバースプロキシ)

- **役割**:
    1.  **SSL/TLS終端**: 443番ポートでHTTPS通信を受け付けます。SSL証明書はLet's Encryptなどで取得し、ボリュームでマウントします。
    2.  **リバースプロキシ**: 受け取ったリクエストを内部のSerenaコンテナ (`http://serena:9121`) に転送します。
    3.  **Basic認証**: 事前に作成した認証ファイル (`.htpasswd`) を用いて、アクセスにユーザー名とパスワードを要求します。
- **設定ファイル例 (`./nginx/conf.d/serena.conf`)**:
    ```nginx
    server {
        listen 80;
        server_name your-domain.com; # あなたのドメイン名に変更
        # SSL化のためのリダイレクト
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com; # あなたのドメイン名に変更

        # SSL証明書のパス
        ssl_certificate /etc/ssl/certs/fullchain.pem;
        ssl_certificate_key /etc/ssl/certs/privkey.pem;

        location / {
            # Basic認証
            auth_basic "Restricted Access";
            auth_basic_user_file /etc/nginx/auth/.htpasswd;

            # Serenaコンテナへのリバースプロキシ設定
            proxy_pass http://serena:9121;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

### D. ログ管理 (CloudWatch Logs)

- `docker-compose.yml` の `logging` ディレクティブで `awslogs` ドライバーを指定することで、コンテナの標準出力が自動的にCloudWatch Logsに転送されます。
- これにより、AWSマネジメントコンソールからログの検索、監視、アラーム設定などが可能になります。
- **注意**: EC2インスタンスには、CloudWatch Logsへの書き込み権限を持つIAMロールをアタッチする必要があります。

---

## 3. 前提条件・準備

- AWSアカウント
- EC2インスタンスにアタッチするドメイン名
- EC2インスタンスにCloudWatch Logsへの書き込み権限を持つIAMロール
