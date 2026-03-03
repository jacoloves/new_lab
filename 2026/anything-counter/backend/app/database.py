from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite:///./counter.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

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
