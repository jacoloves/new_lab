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
