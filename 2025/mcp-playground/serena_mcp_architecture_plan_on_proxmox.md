# Serena MCP リモートホストアーキテクチャプラン (Proxmox + OSS版)

## 1. 概要

このアーキテクチャは、**Proxmox VE** 上の仮想マシン（VM）にDocker環境を構築し、Serena MCPを運用します。ログ収集・監視には、軽量でコンテナ環境と相性の良いオープンソースの **PLGスタック (Promtail, Loki, Grafana)** を採用します。

- **ホスティング**: Proxmox VE上のVM (Ubuntu ServerやDebianを推奨)
- **セキュリティ**: NginxによるSSL/TLS終端とBasic認証
- **ロギング**: Promtailがコンテナログを収集し、Lokiが集約、Grafanaで可視化します。

### 構成図

```
[ローカルマシン (Cline)]
       |
       | (インターネット経由 - HTTPS / Basic認証)
       v
[Proxmox VE ホスト]
+----------------------------------------------------------------+
| [VM: Serena Host (Ubuntu/Debian)]                              |
| +------------------------------------------------------------+ |
| | [Docker Environment]                                       | |
| |                                                            | |
| | +--------------------+  +--------------------------------+ | |
| | | [Nginx コンテナ]     |  | [Serena MCP コンテナ]          | | |
| | | - Port 443         |  | - Port 9121 (internal)         | | |
| | | - SSL/TLS          |  |                                | | |
| | | - Basic Auth       |  |                                | | |
| | +--------+-----------+  +------------------+-------------+ | |
| |          |                                |               | |
| |          +------------> (HTTP) -----------+               | |
| |                                                            | |
| |          +--------------------------------+                | |
| |          | [Promtail コンテナ (Log Collector)] |<--------------+ (Dockerログを収集)
| |          +--------------------------------+                | |
| |                         |                                  | |
| +-------------------------|------------------------------------+ |
+---------------------------|--------------------------------------+
                            | (収集したログをLokiへ転送)
                            v
+----------------------------------------------------------------+
| [VM: Logging Stack (同一VMまたは別VM)]                         |
| +------------------------------------------------------------+ |
| | [Docker Environment]                                       | |
| |                                                            | |
| | +--------------------+  +--------------------------------+ | |
| | | [Loki コンテナ]      |  | [Grafana コンテナ]             | | |
| | | - Log Storage      |  | - Dashboard & Visualization    | | |
| | +--------------------+  +--------------------------------+ | |
| |                                                            | |
| +------------------------------------------------------------+ |
+----------------------------------------------------------------+
```

---

## 2. 各コンポーネントの具体的な設定

### A. ホスト環境

- **仮想化**: Proxmox VE
- **VM**: Ubuntu Server 22.04 LTS や Debian 12 などの安定したLinuxディストリビューションをインストールします。
- **ネットワーク**: VMには固定のプライベートIPアドレスを割り当て、ルーターでポートフォワーディング（80, 443番ポート）を設定します。
- **ファイアウォール**: Proxmoxのファイアウォール機能や、VM内の `ufw` を利用して、必要なポート（SSH, HTTP, HTTPS）のみを開放します。

### B. Docker環境 (`docker-compose.yml`)

Serena MCPとNginxに加え、ログ収集用のPromtailも同じ`docker-compose.yml`で管理します。

```yaml
version: '3.8'

services:
  serena:
    image: ghcr.io/oraios/serena:latest
    container_name: serena_mcp
    restart: always
    command: serena start-mcp-server --transport sse --host 0.0.0.0 --port 9121
    volumes:
      - serena_data:/root/.serena
      - /path/to/your/projects:/workspaces/projects
    logging:
      # Lokiにログを転送するためのDockerドライバー設定
      driver: loki
      options:
        loki-url: "http://<LOKI_HOST_IP>:3100/loki/api/v1/push"

  nginx:
    image: nginx:latest
    container_name: nginx_proxy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/auth:/etc/nginx/auth:ro
      - /path/to/ssl_certs:/etc/ssl/certs:ro
    depends_on:
      - serena
    logging:
      driver: loki
      options:
        loki-url: "http://<LOKI_HOST_IP>:3100/loki/api/v1/push"

volumes:
  serena_data:
```
**注**: 上記の `logging` 設定は、DockerにLokiのロギングドライバープラグインをインストールする必要があります。より簡単な方法として、Promtailコンテナを起動して、Dockerソケットをマウントし、全コンテナのログを自動収集させる構成も一般的です。

### C. ログ管理 (PLGスタック)

- **Promtail**: 各Dockerコンテナのログを収集するエージェントです。ログにラベル（例: `container_name=serena_mcp`）を付与し、Lokiに送信します。
- **Loki**: Promtailから送られてきたログを集約・保存するデータベースです。
- **Grafana**: Lokiをデータソースとして設定し、ログを検索・可視化するためのダッシュボードツールです。

---

## 3. AWS版との比較

| 項目 | AWS版 | Proxmox + OSS版 |
| :--- | :--- | :--- |
| **ホスティング** | AWS EC2 (従量課金) | オンプレミス (初期ハードウェアコスト) |
| **ログ管理** | AWS CloudWatch Logs (従量課金) | Loki + Grafana (OSS, 無料) |
| **運用コスト** | 利用量に応じた変動費 | 電気代、ハードウェア維持費などの固定費 |
| **管理** | AWSマネージド | 自己管理 (Proxmox, VM, OSSの知識が必要) |
