# Step 1: バックエンド基盤（FastAPI + SQLite + SQLAlchemy）

## このステップで作るもの

- FastAPI によるWebサーバーの起動
- SQLite データベースへの接続とテーブル自動作成
- `counters` テーブルと `records` テーブルのモデル定義
- ヘルスチェックエンドポイント (`GET /health`)
- pytest によるモデルテストとエンドポイントテスト

**完了後の状態**: `uvicorn` でサーバーを起動し、`/health` にアクセスすると `{"status": "ok"}` が返る。pytest で全テストがパスする。

## 前提条件

- Python 3.10 以上がインストールされていること
- `uv` または `pip` が使えること
- ターミナル（コマンドライン）が使えること

---

## 1-1. プロジェクトディレクトリの作成

```bash
# プロジェクトのルートディレクトリを作成
$ mkdir -p anything-counter/backend
$ cd anything-counter/backend
```

---

## 1-2. Python仮想環境の作成と有効化

```bash
# uvを使う場合
$ uv venv
$ source .venv/bin/activate

# pipを使う場合
$ python -m venv .venv
$ source .venv/bin/activate
```

---

## 1-3. 依存パッケージの定義

### 作成ファイル: `backend/requirements.txt`

#### このファイルの役割
本番環境で必要なPythonパッケージを定義する。バージョンを固定することで、環境ごとの差異を防ぐ。

#### コード

```text
# FastAPI: Python製の高速Webフレームワーク。型ヒントベースで自動ドキュメント生成機能あり
fastapi==0.115.0
# uvicorn: ASGI対応のWebサーバー。FastAPIアプリを実行するために必要
uvicorn==0.30.0
# SQLAlchemy: PythonのORM（Object-Relational Mapping）。SQLをPythonオブジェクトとして扱える
sqlalchemy==2.0.35
```

### 作成ファイル: `backend/requirements-dev.txt`

#### このファイルの役割
開発・テスト時に追加で必要なパッケージを定義する。`-r requirements.txt` で本番依存も含める。

#### コード

```text
# -r: 別のrequirementsファイルを読み込む。本番用パッケージも開発環境に含める
-r requirements.txt
# pytest: Pythonのテストフレームワーク。テスト関数を自動検出して実行する
pytest==8.3.0
# httpx: 非同期対応HTTPクライアント。FastAPIのTestClientが内部で使用する
httpx==0.27.0
```

### 実行・確認

```bash
# 開発用パッケージをインストール（本番用も含まれる）
$ pip install -r requirements-dev.txt

# インストール確認
$ pip list | grep -E "fastapi|uvicorn|sqlalchemy|pytest|httpx"
fastapi        0.115.0
httpx          0.27.0
pytest         8.3.0
SQLAlchemy     2.0.35
uvicorn        0.30.0
```

---

## 1-4. アプリケーションパッケージの初期化

### 作成ファイル: `backend/app/__init__.py`

#### このファイルの役割
`app` ディレクトリをPythonパッケージとして認識させる。中身は空でよい。

#### コード

```python
# 空ファイル — Pythonパッケージとして認識させるために必要
# このファイルがあることで `from app.xxx import yyy` という記法が使える
```

### 実行・確認

```bash
# ディレクトリ構造を確認
$ mkdir -p app
$ touch app/__init__.py
$ ls app/
__init__.py
```

---

## 1-5. データベース接続の設定

### 作成ファイル: `backend/app/database.py`

#### このファイルの役割
SQLite データベースへの接続エンジン、セッションファクトリ、ベースクラス、そしてFastAPIのDependency Injection用のジェネレータを定義する。アプリ全体のDB接続をこのファイルに集約する。

#### コード

```python
"""データベース接続とセッション管理"""

# create_engine: SQLAlchemy のDB接続エンジンを作成する関数
from sqlalchemy import create_engine
# sessionmaker: DBセッション（トランザクション単位の操作）を生成するファクトリ
# DeclarativeBase: SQLAlchemy 2.0 の推奨パターン。全モデルの親クラスになる
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLiteのファイルパス。sqlite:///./counter.db は backend/ 直下に counter.db を作成する
# check_same_thread=False: SQLiteはデフォルトで同一スレッドでしか使えないが、
# FastAPIは複数スレッドでリクエストを処理するため、この制約を解除する
SQLALCHEMY_DATABASE_URL = "sqlite:///./counter.db"

# DB接続エンジンを作成
# connect_args: SQLite固有の接続オプションを渡す
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# セッションファクトリの作成
# autocommit=False: 明示的にcommit()を呼ぶまでDBに反映しない（データ整合性の確保）
# autoflush=False: 明示的にflush()を呼ぶまでSQLを発行しない（パフォーマンス向上）
# bind=engine: このセッションが使うDB接続エンジンを指定
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """全モデルの基底クラス。SQLAlchemy 2.0の推奨パターン。
    全てのテーブルモデル（Counter, Record）はこのクラスを継承する。"""
    pass


def get_db():
    """リクエストごとにDBセッションを生成し、終了時に自動クローズするジェネレータ。
    FastAPIのDepends()で使用する。

    使い方:
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            ...

    try/finallyパターンにより、例外が発生してもセッションは必ず閉じられる。
    """
    # 新しいDBセッションを生成
    db = SessionLocal()
    try:
        # yieldでセッションを返す（ジェネレータ）
        # FastAPIがこのセッションをエンドポイント関数に注入する
        yield db
    finally:
        # リクエスト完了後（正常終了でも例外でも）セッションを閉じる
        db.close()
```

### 実行・確認

```bash
# 構文エラーがないことを確認
$ python -c "from app.database import Base, engine, get_db; print('OK')"
OK
```

---

## 1-6. テーブルモデルの定義

### 作成ファイル: `backend/app/models.py`

#### このファイルの役割
`counters` テーブルと `records` テーブルのSQLAlchemyモデルを定義する。モデル定義がそのままDBのテーブル構造になる。

#### コード

```python
"""SQLAlchemyモデル定義 — countersとrecordsの2テーブル"""

# Column: テーブルのカラム（列）を定義するクラス
# Integer, Text: カラムの型
# ForeignKey: 外部キー制約（別テーブルのIDを参照）
# UniqueConstraint: 複合ユニーク制約（複数カラムの組み合わせで一意性を保証）
from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint
# func.now(): SQL関数 CURRENT_TIMESTAMP を呼び出す
from sqlalchemy.sql import func
# relationship: テーブル間のリレーション（1対多など）を定義
from sqlalchemy.orm import relationship

# 同じパッケージ内の database.py から Base をインポート
from .database import Base


class Counter(Base):
    """習慣カウンターを表すテーブル。1行 = 1つの習慣（例: 筋トレ、読書）"""

    # テーブル名を明示的に指定。省略するとクラス名がそのまま使われる
    __tablename__ = "counters"

    # id: 主キー。autoincrement=Trueで自動採番（1, 2, 3, ...）
    id = Column(Integer, primary_key=True, autoincrement=True)
    # name: カウンター名。nullable=Falseで空を許可しない
    name = Column(Text, nullable=False)
    # created_at: 作成日時。server_default=func.now()でDB側が自動設定する
    created_at = Column(Text, nullable=False, server_default=func.now())
    # sort_order: 表示順序。将来のドラッグ&ドロップ並べ替え用。デフォルト0
    sort_order = Column(Integer, nullable=False, default=0)

    # records: Recordモデルとの1対多リレーション
    # back_populates="counter": Record側の counter 属性と双方向に紐づく
    # cascade="all, delete-orphan": Counter削除時にRecordも自動削除（孤児レコード防止）
    records = relationship(
        "Record", back_populates="counter", cascade="all, delete-orphan"
    )


class Record(Base):
    """実行記録を表すテーブル。1行 = ある日にある習慣を実行した記録"""

    __tablename__ = "records"

    # id: 主キー。自動採番
    id = Column(Integer, primary_key=True, autoincrement=True)
    # counter_id: 外部キー。counters.idを参照
    # ondelete="CASCADE": 参照先（Counter）が削除されたら、このレコードも削除
    counter_id = Column(
        Integer, ForeignKey("counters.id", ondelete="CASCADE"), nullable=False
    )
    # date: 実行日。"YYYY-MM-DD"形式のテキスト（SQLiteに日付型はないため）
    date = Column(Text, nullable=False)
    # created_at: 作成日時。DB側で自動設定
    created_at = Column(Text, nullable=False, server_default=func.now())

    # counter: Counterモデルとのリレーション（多対1）
    # back_populates="records": Counter側の records 属性と双方向に紐づく
    counter = relationship("Counter", back_populates="records")

    # テーブルレベルの制約を定義
    # UniqueConstraint: counter_idとdateの組み合わせで一意性を保証
    # → 同じカウンターで同じ日に2回記録できないようにする
    __table_args__ = (
        UniqueConstraint("counter_id", "date", name="uq_counter_date"),
    )
```

### 実行・確認

```bash
# モデルが正しく読み込めることを確認
$ python -c "from app.models import Counter, Record; print('Counter:', Counter.__tablename__); print('Record:', Record.__tablename__)"
Counter: counters
Record: records
```

---

## 1-7. FastAPIアプリケーションのエントリポイント

### 作成ファイル: `backend/app/main.py`

#### このファイルの役割
FastAPIアプリケーションのインスタンスを作成し、起動時にテーブルを自動生成する。ヘルスチェック用のエンドポイントも定義する。

#### コード

```python
"""FastAPIアプリケーションのエントリポイント"""

# FastAPI: Webアプリケーションフレームワークのメインクラス
from fastapi import FastAPI

# 同じパッケージのdatabase.pyからDB接続エンジンとBaseクラスをインポート
from .database import engine, Base

# アプリケーション起動時にテーブルを自動作成
# models.pyで定義したCounter, Recordテーブルが存在しなければ作成する
# すでに存在する場合は何もしない（既存データは消えない）
Base.metadata.create_all(bind=engine)

# FastAPIアプリケーションのインスタンスを作成
# title: Swagger UIに表示されるAPI名
# version: APIのバージョン番号
app = FastAPI(title="Anything Counter", version="0.1.0")


@app.get("/health")
def health_check():
    """ヘルスチェック用エンドポイント。
    サーバーが正常に動作しているか確認するために使用する。
    本番環境ではロードバランサーやモニタリングツールが定期的にアクセスする。"""
    return {"status": "ok"}
```

### 実行・確認

```bash
# サーバーを起動（Ctrl+Cで停止）
$ uvicorn app.main:app --reload --port 8000

# 別のターミナルからヘルスチェック
$ curl http://localhost:8000/health
{"status":"ok"}

# Swagger UI（自動生成されるAPIドキュメント）をブラウザで確認
# http://localhost:8000/docs
```

**期待される出力（サーバー起動時）:**

```
INFO:     Will watch for changes in these directories: ['/path/to/backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 1-8. テスト基盤の構築

### 作成ファイル: `backend/tests/__init__.py`

#### このファイルの役割
`tests` ディレクトリをPythonパッケージとして認識させる。

#### コード

```python
# 空ファイル — Pythonパッケージとして認識させるために必要
```

### 作成ファイル: `backend/tests/conftest.py`

#### このファイルの役割
pytest のフィクスチャ（テスト用の共通セットアップ）を定義する。インメモリSQLiteを使い、テストごとにDBを初期化して独立性を保証する。

#### コード

```python
"""テスト共通フィクスチャ — インメモリSQLiteとTestClient"""

# pytest: テストフレームワーク。fixtureデコレータでセットアップ関数を定義できる
import pytest
# TestClient: FastAPIアプリに対してHTTPリクエストを送るテスト用クライアント
from fastapi.testclient import TestClient
# create_engine: テスト用のDB接続エンジンを作成
from sqlalchemy import create_engine
# sessionmaker: テスト用のセッションファクトリを作成
from sqlalchemy.orm import sessionmaker
# StaticPool: インメモリDBの接続を使い回すためのプール戦略
from sqlalchemy.pool import StaticPool

# テスト対象のモジュールからインポート
from app.database import Base, get_db
from app.main import app

# テスト用のインメモリSQLiteエンジン
# "sqlite://": パスなし → メモリ上にDBを作成（ファイルを汚さない）
# StaticPool: 通常、インメモリDBは接続を閉じるとデータが消える
#             StaticPoolで接続を共有することで、テスト中はデータを保持する
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
# テスト用のセッションファクトリ（本番とは別のエンジンを使う）
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    """テスト用DBセッション。テストごとにテーブルを作り直す。

    フロー:
    1. create_all: テーブルを作成
    2. yield session: テスト関数にセッションを渡す
    3. session.close(): セッションを閉じる
    4. drop_all: テーブルを全削除（次のテストに影響を与えない）
    """
    # テスト開始前: 全テーブルを作成
    Base.metadata.create_all(bind=engine)
    # 新しいセッションを生成
    session = TestingSessionLocal()
    try:
        # テスト関数にセッションを渡す
        yield session
    finally:
        # テスト終了後: セッションを閉じてテーブルを全削除
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    """テスト用FastAPIクライアント。本番DBをテスト用DBに差し替える。

    dependency_overrides: FastAPI公式のDI差し替えパターン。
    本番のget_db()が返すセッションを、テスト用のセッションに置き換える。
    """
    # get_db を上書きする関数を定義
    def override_get_db():
        # テスト用のdbセッションをそのまま返す
        yield db

    # FastAPIのDIを上書き: get_db → override_get_db
    app.dependency_overrides[get_db] = override_get_db
    # TestClientを使ってFastAPIアプリにリクエストを送れるようにする
    with TestClient(app) as c:
        yield c
    # テスト終了後: DI上書きをクリア（他のテストに影響を与えない）
    app.dependency_overrides.clear()
```

### 実行・確認

```bash
# テストディレクトリの構造を確認
$ mkdir -p tests
$ ls tests/
__init__.py  conftest.py
```

---

## 1-9. モデルテストの作成

### 作成ファイル: `backend/tests/test_models.py`

#### このファイルの役割
Counter モデルと Record モデルが正しく動作するかテストする。作成・取得・カスケード削除・ユニーク制約を検証する。

#### コード

```python
"""モデルのテスト — テーブル作成とレコード挿入の確認"""

# テスト対象のモデルをインポート
from app.models import Counter, Record


class TestCounterModel:
    """Counterモデルのテスト"""

    def test_カウンターを作成できる(self, db):
        """カウンターを作成してDBに保存し、取得できることを確認"""
        # Counterインスタンスを作成（nameのみ指定、他はデフォルト値）
        counter = Counter(name="筋トレ")
        # セッションに追加（この時点ではまだDBに保存されていない）
        db.add(counter)
        # DBに保存（コミット）
        db.commit()
        # DBから最新の状態を読み込み直す（idやcreated_atが設定される）
        db.refresh(counter)

        # idが自動採番されていることを確認（Noneではない）
        assert counter.id is not None
        # nameが正しく保存されていることを確認
        assert counter.name == "筋トレ"
        # sort_orderのデフォルト値が0であることを確認
        assert counter.sort_order == 0

    def test_複数カウンターを作成できる(self, db):
        """複数のカウンターを作成して一覧取得できることを確認"""
        # 2つのカウンターをセッションに追加
        db.add(Counter(name="筋トレ"))
        db.add(Counter(name="読書"))
        # まとめてコミット
        db.commit()

        # 全カウンターを取得
        counters = db.query(Counter).all()
        # 2件取得できることを確認
        assert len(counters) == 2


class TestRecordModel:
    """Recordモデルのテスト"""

    def test_実行記録を作成できる(self, db):
        """カウンターに紐づく実行記録を作成できることを確認"""
        # まずカウンターを作成（Recordはカウンターに紐づくため）
        counter = Counter(name="筋トレ")
        db.add(counter)
        db.commit()

        # カウンターに紐づく実行記録を作成
        record = Record(counter_id=counter.id, date="2026-02-23")
        db.add(record)
        db.commit()
        db.refresh(record)

        # 各フィールドが正しく保存されていることを確認
        assert record.id is not None
        assert record.counter_id == counter.id
        assert record.date == "2026-02-23"

    def test_カウンター削除時に記録も削除される(self, db):
        """cascade deleteが正しく動作することを確認。
        Counter削除 → 関連するRecordも自動削除されるべき。"""
        # カウンターと記録を作成
        counter = Counter(name="筋トレ")
        db.add(counter)
        db.commit()

        record = Record(counter_id=counter.id, date="2026-02-23")
        db.add(record)
        db.commit()

        # カウンターを削除
        db.delete(counter)
        db.commit()

        # 関連する記録も一緒に削除されていることを確認
        records = db.query(Record).all()
        assert len(records) == 0

    def test_同じ日に同じカウンターで重複記録できない(self, db):
        """UniqueConstraint(counter_id, date)が正しく動作することを確認。
        同じカウンターの同じ日に2つ目の記録を作ろうとするとエラーになるべき。"""
        # IntegrityError: DB制約違反時に発生する例外
        from sqlalchemy.exc import IntegrityError

        # カウンターと1つ目の記録を作成
        counter = Counter(name="筋トレ")
        db.add(counter)
        db.commit()

        # 1つ目の記録（成功するはず）
        db.add(Record(counter_id=counter.id, date="2026-02-23"))
        db.commit()

        # 2つ目の同日記録（IntegrityErrorが発生するはず）
        db.add(Record(counter_id=counter.id, date="2026-02-23"))
        # pytest.raisesで特定の例外が発生することを検証
        import pytest
        with pytest.raises(IntegrityError):
            db.commit()
```

---

## 1-10. ヘルスチェックテストの作成

### 作成ファイル: `backend/tests/test_health.py`

#### このファイルの役割
FastAPI アプリの `/health` エンドポイントが正しく動作するかテストする。

#### コード

```python
"""ヘルスチェックエンドポイントのテスト"""


def test_ヘルスチェックが正常に動作する(client):
    """GET /health が {"status": "ok"} を返すことを確認。
    clientフィクスチャはconftest.pyで定義されたTestClient。"""
    # GETリクエストを /health に送信
    response = client.get("/health")
    # HTTPステータスコードが200（成功）であることを確認
    assert response.status_code == 200
    # レスポンスのJSONボディが期待通りであることを確認
    assert response.json() == {"status": "ok"}
```

---

## テスト実行

```bash
# backendディレクトリで実行
$ cd backend

# テストを詳細モード(-v)で実行
$ pytest -v

# 期待される出力:
tests/test_health.py::test_ヘルスチェックが正常に動作する PASSED
tests/test_models.py::TestCounterModel::test_カウンターを作成できる PASSED
tests/test_models.py::TestCounterModel::test_複数カウンターを作成できる PASSED
tests/test_models.py::TestRecordModel::test_実行記録を作成できる PASSED
tests/test_models.py::TestRecordModel::test_カウンター削除時に記録も削除される PASSED
tests/test_models.py::TestRecordModel::test_同じ日に同じカウンターで重複記録できない PASSED

========================= 6 passed =========================
```

---

## このステップのディレクトリ構造

```
backend/
├── requirements.txt          # 本番依存パッケージ
├── requirements-dev.txt      # 開発用追加パッケージ
├── app/
│   ├── __init__.py           # パッケージ初期化（空）
│   ├── database.py           # DB接続・セッション管理
│   ├── models.py             # テーブルモデル定義
│   └── main.py               # FastAPIエントリポイント
└── tests/
    ├── __init__.py            # パッケージ初期化（空）
    ├── conftest.py            # テスト共通フィクスチャ
    ├── test_models.py         # モデルテスト
    └── test_health.py         # ヘルスチェックテスト
```

---

## このステップの完了チェックリスト

- [ ] `pip install -r requirements-dev.txt` が成功する
- [ ] `python -c "from app.models import Counter, Record"` がエラーなく実行できる
- [ ] `uvicorn app.main:app --port 8000` でサーバーが起動する
- [ ] `curl http://localhost:8000/health` で `{"status":"ok"}` が返る
- [ ] `pytest -v` で6件全てのテストがパスする
- [ ] `backend/counter.db` ファイルが自動生成される（サーバー起動後）
