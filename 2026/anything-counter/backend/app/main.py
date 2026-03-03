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
