  それでは、Step 1のコードを提示します。各ファイルを順番に説明していきます。

  1-1. requirements.txt

  fastapi==0.115.0
  uvicorn==0.30.0
  sqlalchemy==2.0.35

  - fastapi: Webフレームワーク本体
  - uvicorn: ASGI サーバー（FastAPIを動かすために必要）
  - sqlalchemy: ORM（DBとPythonオブジェクトの橋渡し）

  1-2. requirements-dev.txt

  -r requirements.txt
  pytest==8.3.0
  httpx==0.27.0

  - pytest: テストフレームワーク
  - httpx: FastAPIのTestClientに必要（非同期HTTPクライアント）
  - -r requirements.txt: 本番依存も含める

  1-3. app/database.py

  """データベース接続とセッション管理"""
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker, DeclarativeBase

  # SQLiteファイルをbackend/ディレクトリ直下に作成
  # check_same_thread=False: FastAPIのマルチスレッド環境で必要
  SQLALCHEMY_DATABASE_URL = "sqlite:///./counter.db"

  engine = create_engine(
      SQLALCHEMY_DATABASE_URL,
      connect_args={"check_same_thread": False},
  )

  # autocommit=False: 明示的にcommit()するまでDBに反映しない（データ整合性の確保）
  # autoflush=False: 明示的にflush()するまでSQLを発行しない（パフォーマンス向上）
  SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


  class Base(DeclarativeBase):
      """全モデルの基底クラス。SQLAlchemy 2.0の推奨パターン"""
      pass


  def get_db():
      """リクエストごとにDBセッションを生成し、終了時に自動クローズするジェネレータ。
      FastAPIのDepends()で使用する。"""
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()

  各行の役割:
  - create_engine: SQLiteへの接続エンジンを作成。check_same_thread=FalseはSQLiteの制約回避（FastAPIは複数スレッドでリクエストを処理するため）
  - SessionLocal: セッションファクトリ。各リクエストで新しいセッションを作る
  - Base: 全テーブルモデルの親クラス。SQLAlchemy 2.0のDeclarativeBaseパターン
  - get_db(): FastAPIのDependency Injectionで使うジェネレータ。try/finallyでセッションの確実なクリーンアップを保証

  1-4. app/models.py

  """SQLAlchemyモデル定義 — countersとrecordsの2テーブル"""
  from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint
  from sqlalchemy.sql import func
  from sqlalchemy.orm import relationship

  from .database import Base


  class Counter(Base):
      """習慣カウンターを表すテーブル。1行 = 1つの習慣（例: 筋トレ、読書）"""
      __tablename__ = "counters"

      id = Column(Integer, primary_key=True, autoincrement=True)
      name = Column(Text, nullable=False)  # カウンター名
      created_at = Column(Text, nullable=False, server_default=func.now())  # 作成日時
      sort_order = Column(Integer, nullable=False, default=0)  # 表示順序（将来の並べ替え用）

      # カウンター削除時に関連recordsも自動削除される（cascade）
      records = relationship("Record", back_populates="counter", cascade="all, delete-orphan")


  class Record(Base):
      """実行記録を表すテーブル。1行 = ある日にある習慣を実行した記録"""
      __tablename__ = "records"

      id = Column(Integer, primary_key=True, autoincrement=True)
      counter_id = Column(Integer, ForeignKey("counters.id", ondelete="CASCADE"), nullable=False)
      date = Column(Text, nullable=False)  # "YYYY-MM-DD"形式
      created_at = Column(Text, nullable=False, server_default=func.now())

      counter = relationship("Counter", back_populates="records")

      # 同じカウンターで同じ日に2回記録できないようにする
      __table_args__ = (
          UniqueConstraint("counter_id", "date", name="uq_counter_date"),
      )

  設計ポイント:
  - relationship + cascade="all, delete-orphan": カウンター削除時にレコードも自動削除。孤児レコードを防止
  - UniqueConstraint("counter_id", "date"): 同日重複をDB層で防止（アプリ層のバリデーションだけでは競合状態に対応できない）
  - server_default=func.now(): DB側でタイムスタンプを生成（アプリ側の時計ずれを回避）

  1-5. app/main.py

  """FastAPIアプリケーションのエントリポイント"""
  from fastapi import FastAPI

  from .database import engine, Base

  # アプリケーション起動時にテーブルを自動作成
  Base.metadata.create_all(bind=engine)

  app = FastAPI(title="Anything Counter", version="0.1.0")


  @app.get("/health")
  def health_check():
      """ヘルスチェック用エンドポイント。サーバーが正常に動作しているか確認する"""
      return {"status": "ok"}

  各行の役割:
  - Base.metadata.create_all(bind=engine): models.pyで定義したテーブルが存在しなければ作成する（既存なら何もしない）
  - /health: サーバー起動確認用の最小エンドポイント

  1-6. app/__init__.py


  （空ファイル — Pythonパッケージとして認識させるために必要）

  1-7. tests/conftest.py

  """テスト共通フィクスチャ — インメモリSQLiteとTestClient"""
  import pytest
  from fastapi.testclient import TestClient
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker
  from sqlalchemy.pool import StaticPool

  from app.database import Base, get_db
  from app.main import app

  # インメモリSQLite: テストごとにDBが初期化され、テスト間の独立性を保証
  # StaticPool: インメモリDBの接続を使い回す（接続が切れるとデータが消えるため）
  engine = create_engine(
      "sqlite://",
      connect_args={"check_same_thread": False},
      poolclass=StaticPool,
  )
  TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


  @pytest.fixture()
  def db():
      """テスト用DBセッション。テストごとにテーブルを作り直す"""
      Base.metadata.create_all(bind=engine)
      session = TestingSessionLocal()
      try:
          yield session
      finally:
          session.close()
          Base.metadata.drop_all(bind=engine)


  @pytest.fixture()
  def client(db):
      """テスト用FastAPIクライアント。get_dbをオーバーライドしてテスト用DBを注入"""
      def override_get_db():
          yield db

      app.dependency_overrides[get_db] = override_get_db
      with TestClient(app) as c:
          yield c
      app.dependency_overrides.clear()

  設計ポイント:
  - sqlite://（パスなし）: インメモリDBを使用。ファイルを汚さない
  - StaticPool: インメモリDBは接続を閉じるとデータが消えるため、接続を共有する
  - dependency_overrides: FastAPIの公式パターン。本番のDBを差し替えてテスト用DBを注入
  - drop_all: テスト後にテーブルを削除し、次のテストに影響を与えない

  1-8. tests/__init__.py


  （空ファイル）

  1-9. tests/test_models.py

  """モデルのテスト — テーブル作成とレコード挿入の確認"""
  from app.models import Counter, Record


  class TestCounterModel:
      """Counterモデルのテスト"""

      def test_カウンターを作成できる(self, db):
          """カウンターを作成してDBに保存し、取得できることを確認"""
          counter = Counter(name="筋トレ")
          db.add(counter)
          db.commit()
          db.refresh(counter)

          assert counter.id is not None
          assert counter.name == "筋トレ"
          assert counter.sort_order == 0

      def test_複数カウンターを作成できる(self, db):
          """複数のカウンターを作成して一覧取得できることを確認"""
          db.add(Counter(name="筋トレ"))
          db.add(Counter(name="読書"))
          db.commit()

          counters = db.query(Counter).all()
          assert len(counters) == 2


  class TestRecordModel:
      """Recordモデルのテスト"""

      def test_実行記録を作成できる(self, db):
          """カウンターに紐づく実行記録を作成できることを確認"""
          counter = Counter(name="筋トレ")
          db.add(counter)
          db.commit()

          record = Record(counter_id=counter.id, date="2026-02-23")
          db.add(record)
          db.commit()
          db.refresh(record)

          assert record.id is not None
          assert record.counter_id == counter.id
          assert record.date == "2026-02-23"

      def test_カウンター削除時に記録も削除される(self, db):
          """cascade deleteが正しく動作することを確認"""
          counter = Counter(name="筋トレ")
          db.add(counter)
          db.commit()

          record = Record(counter_id=counter.id, date="2026-02-23")
          db.add(record)
          db.commit()

          db.delete(counter)
          db.commit()

          records = db.query(Record).all()
          assert len(records) == 0

      def test_同じ日に同じカウンターで重複記録できない(self, db):
          """UniqueConstraintが正しく動作することを確認"""
          from sqlalchemy.exc import IntegrityError

          counter = Counter(name="筋トレ")
          db.add(counter)
          db.commit()

          db.add(Record(counter_id=counter.id, date="2026-02-23"))
          db.commit()

          db.add(Record(counter_id=counter.id, date="2026-02-23"))
          with pytest.raises(IntegrityError):
              db.commit()


  # pytestのインポート（test_同じ日〜で使用）
  import pytest

  1-10. tests/test_health.py（main.pyのテスト）

  """ヘルスチェックエンドポイントのテスト"""


  def test_ヘルスチェックが正常に動作する(client):
      """GET /health が {"status": "ok"} を返すことを確認"""
      response = client.get("/health")
      assert response.status_code == 200
      assert response.json() == {"status": "ok"}

  ---
 
