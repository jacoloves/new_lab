# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 開発コマンド

```bash
# 依存関係のインストール（uvを使用）
uv sync

# シナリオの実行例
python chap4/scenario_chap4a.py
python chap5/scenario_chap5a.py
```

各シナリオファイルは `sys.path.append` でリポジトリルートを追加しているため、**リポジトリルートから実行**する必要がある。

## アーキテクチャ概要

本リポジトリは **イベント駆動型ネットワークシミュレーター** の実装で、書籍の各章（chap2〜chap5）の演習シナリオから `network/` パッケージを利用する構成になっている。

### `network/` パッケージの構成

```
NetworkEventScheduler  ← シミュレーション全体の司令塔
       ↓ イベントキュー（heapq）
  Node / Switch / Router  ← ネットワーク機器
       ↓ パケットの送受信
    Link  ← 双方向リンク（帯域・遅延・ロス率・キューを持つ）
       ↓
  Packet / BPDU  ← パケット表現
```

**`NetworkEventScheduler`** (`scheduler.py`)
- `heapq` によるイベントキューで時刻順にコールバックを実行
- NetworkX グラフでトポロジーを管理し、matplotlib で可視化
- `log_enabled=True` でパケットログを収集、スループット・遅延ヒストグラムを生成可能
- `verbose` / `stp_verbose` / `routing_verbose` フラグでデバッグ出力を制御

**`Link`** (`link.py`)
- node_x → node_y, node_y → node_x の双方向に独立したパケットキューを持つ
- 転送時間 = パケットサイズ × 8 / bandwidth でシリアル化遅延を模倣
- `loss_rate` でランダムパケットロスをシミュレート

**`Node`** (`node.py`)
- MAC アドレス + CIDR 表記 IP アドレスを持つ端末
- `send_packet()` でフラグメンテーションを処理し、`receive_packet()` で再組み立て
- `set_traffic()` で指定ビットレート・期間のトラフィックを生成

**`Switch`** (`switch.py`)
- MAC アドレステーブル（フォワーディングテーブル）によるL2転送
- BPDU 交換による **STP（スパニングツリープロトコル）** を実装
- リンク状態は `"initial"` → `"forwarding"` または `"blocking"` に遷移

**`Router`** (`router.py`)
- 静的ルーティングテーブル（CIDR → next_hop, link）によるL3転送
- 複数 IP アドレスを持ち、`Link` 生成時に同一サブネットの IP ペアを自動選択

**`Packet` / `BPDU`** (`packet.py`)
- ヘッダに source/destination MAC・IP、TTL、フラグメント情報を保持
- `BPDU` は STP 制御パケット（root_id, bridge_id, path_cost）

### シナリオファイルの構造

各 `chap*/scenario_*.py` は以下の流れで記述される：

1. `NetworkEventScheduler` を生成
2. `Node` / `Switch` / `Router` を生成（スケジューラに登録）
3. `Link` で機器を接続（生成時に双方の `add_link()` が呼ばれる）
4. `node.set_traffic()` でトラフィックをスケジュール
5. `network_event_scheduler.run()` でシミュレーション実行
6. ログ・統計・グラフを出力
