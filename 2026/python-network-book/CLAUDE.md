# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 開発コマンド

```bash
# 依存関係のインストール（uvを使用）
uv sync

# シナリオの実行（必ずリポジトリルートから実行すること）
python chap4/scenario_chap4a.py
python chap12/scenario_chap12a.py
```

各シナリオファイルは `sys.path.append(os.path.join(os.path.dirname(__file__), ".."))` でリポジトリルートを追加しているため、**リポジトリルートから実行**する必要がある。

## アーキテクチャ概要

本リポジトリは **イベント駆動型ネットワークシミュレーター** の実装で、書籍の各章（chap3〜chap13）の演習シナリオから `network/` パッケージを利用する構成になっている。

### シナリオとテストの違い

`scenario_chapNa.py` / `scenario_chapNb.py` は演習シナリオ、`scenario_chapNtest*.py` は動作確認用スクリプト。どちらも **pytest ではなく standalone スクリプト**で、`python <path>` で直接実行する。自動テストフレームワークは存在しない。

### `network/` パッケージの構成

```
NetworkEventScheduler  ← シミュレーション全体の司令塔
       ↓ イベントキュー（heapq）
  Node / Switch / Router / Server  ← ネットワーク機器
       ↓ パケットの送受信
    Link  ← 双方向リンク（帯域・遅延・ロス率・キューを持つ）
       ↓
  Packet / BPDU / ARPPacket / TCPPacket / DNSPacket / DHCPPacket  ← パケット表現
```

### 各クラスの役割

**`NetworkEventScheduler`** (`scheduler.py`)
- `heapq` によるイベントキューで時刻順にコールバックを実行
- NetworkX グラフでトポロジーを管理し、`draw()` で matplotlib 可視化
- `log_enabled=True` でパケットログを収集、`generate_summary()` / `generate_throughput_graph()` / `generate_delay_histogram()` で統計・グラフを出力
- デバッグフラグ: `verbose` / `stp_verbose` / `routing_verbose` / `nat_verbose` / `tcp_verbose` / `link_verbose`
- `run_until(time)` で指定時刻まで実行、`run()` で全イベント完了まで実行
- `seed` 指定で乱数シードを固定し再現性を確保（各 Node/Link も同じシードを共有）

**`Link`** (`link.py`)
- node_x → node_y, node_y → node_x の双方向に独立した **優先度付きキュー**（`defaultdict(list)`）を持つ
- DSCP 値から `Packet.get_priority()` で 0〜7 の優先度を算出し、高優先度パケットを先に転送
- 転送時間 = パケットサイズ × 8 / bandwidth でシリアル化遅延を模倣
- `loss_rate` は UDPPacket と TCP PSH パケットのみに適用（制御パケットはドロップしない）

**`Node`** (`node.py`)
- MAC アドレス + CIDR 表記 IP アドレスを持つ端末
- `send_packet()` でフラグメンテーション（MTU=1500 デフォルト）を処理し、`receive_packet()` で再組み立て
- `set_traffic()` で指定ビットレート・期間の UDP トラフィックを生成
- `start_tcp_traffic(destination_url, ...)` で DNS 解決 → ARP → TCP 接続 → データ転送を自動実行
- `start_udp_traffic(destination_url, bitrate, start_time, duration, header_size, payload_size, dscp)` で DSCP 値付き UDP トラフィックを生成（QoS 検証用）
- DHCP クライアント機能（起動時に `schedule_dhcp_packet()` が呼ばれる）
- ARP テーブル・DNS キャッシュ・TCP 接続状態・フラグメント再組み立てバッファを保持

**`Switch`** (`switch.py`)
- MAC アドレステーブル（フォワーディングテーブル）によるL2転送
- BPDU 交換による **STP（スパニングツリープロトコル）** を実装
- リンク状態は `"initial"` → `"forwarding"` または `"blocking"` に遷移

**`Router`** (`router.py`)
- 複数 IP アドレスを持ち、`Link` 生成時に同一サブネットの IP ペアを自動選択してインタフェースに割り当て
- **OSPF** の Hello パケットと LSA（Link State Advertisement）交換による動的ルーティングを実装
- **NAT** 機能あり（`nat_enabled=True`, `external_ip` 指定で有効化）
- ARP テーブルを保持し、未知の宛先 MAC に対して ARP を送信してパケットをキューイング

**`Server`** (`server.py`) — 3 クラス構成
- `Server`（基底）: ARP 応答のみ実装
- `DNSServer`: `add_dns_record(domain, ip)` でAレコードを登録、DNS クエリに応答
- `DHCPServer`: IP プールを管理し DISCOVER/REQUEST/ACK シーケンスを処理

**`NetworkGraph`** (`graph.py`)
- NetworkX + matplotlib によるトポロジー描画（エッジ幅=帯域幅のlog、エッジ色=遅延）

### シナリオファイルの構造

各 `chap*/scenario_*.py` は以下の流れで記述される：

1. `NetworkEventScheduler` を生成
2. `Node` / `Switch` / `Router` / `DNSServer` / `DHCPServer` を生成（スケジューラに登録）
3. `Link` で機器を接続（生成時に双方の `add_link()` が自動呼び出し）
4. 必要に応じて静的ルーティングや DNS レコード・DHCP 使用済み IP を設定
5. `node.set_traffic()` / `node.start_tcp_traffic()` / `node.start_udp_traffic()` でトラフィックをスケジュール
6. `network_event_scheduler.run()` / `run_until()` でシミュレーション実行
7. 各ノードの状態表示・ログ・統計・グラフを出力

### 章ごとの主題

| 章 | 主題 |
|----|------|
| chap3 | 基本的なパケット転送・Link のキューイング |
| chap4 | スイッチ・L2転送 |
| chap5 | STP（スパニングツリープロトコル） |
| chap6 | ルーター・L3転送・ARP |
| chap7 | IP フラグメンテーションと再組み立て |
| chap8 | OSPF による動的ルーティング |
| chap9 | NAT |
| chap10 | DNS |
| chap11 | DHCP |
| chap12 | TCP（スロースタート・輻輳制御・DNS/DHCP 統合） |
| chap13 | QoS・DSCP 優先度付きキューイング・UDP トラフィック整形 |
