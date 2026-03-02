# Step 2: バックエンドAPI実装（スキーマ・CRUD・ルーター）

## このステップで作るもの

- Pydantic スキーマ（リクエスト/レスポンスの型定義）
- CRUD 関数（データベース操作ロジック）
- カウンター API（一覧・作成・削除）
- 記録 API（月別取得・作成・削除 + 日付バリデーション）
- CORS 設定（フロントエンドからのアクセス許可）

**完了後の状態**: `curl` でカウンターの作成・一覧取得・削除、記録の作成・月別取得・削除ができる。日付バリデーション（未来日拒否・3日前超拒否・重複拒否）が動作する。

## 前提条件

- Step 1 が完了していること（`pytest -v` で全テストパス）
- `backend/` ディレクトリにいること
- 仮想環境が有効化されていること

---

## 2-1. Pydantic スキーマの定義

### 作成ファイル: `backend/app/schemas.py`

#### このファイルの役割
APIのリクエストボディとレスポンスボディの型を定義する。FastAPIはPydanticスキーマを使ってリクエストの自動バリデーションとレスポンスのシリアライズを行う。

#### コード

```python
"""Pydanticスキーマ — APIのリクエスト/レスポンス型定義"""

# BaseModel: Pydanticの基底クラス。データバリデーションとシリアライズを提供
from pydantic import BaseModel


class CounterCreate(BaseModel):
    """カウンター作成リクエストのスキーマ。
    POST /api/counters のリクエストボディとして使用。"""
    # name: カウンター名。文字列型で必須
    name: str


class CounterResponse(BaseModel):
    """カウンターレスポンスのスキーマ。
    GET /api/counters のレスポンスとして使用。"""
    # id: データベースが自動採番するカウンターID
    id: int
    # name: カウンター名
    name: str
    # created_at: 作成日時（ISO8601形式の文字列）
    created_at: str
    # sort_order: 表示順序
    sort_order: int
    # today_done: 今日の記録が存在するかどうか（APIレスポンス時に算出する仮想フィールド）
    today_done: bool

    class Config:
        """Pydanticの設定クラス"""
        # from_attributes=True: SQLAlchemyモデルのインスタンスから直接変換可能にする
        # （旧orm_mode = True に相当）
        from_attributes = True


class RecordCreate(BaseModel):
    """実行記録作成リクエストのスキーマ。
    POST /api/counters/{id}/records のリクエストボディとして使用。"""
    # date: 実行日。"YYYY-MM-DD"形式の文字列
    date: str


class RecordResponse(BaseModel):
    """実行記録レスポンスのスキーマ。
    GET /api/counters/{id}/records のレスポンスとして使用。"""
    # id: データベースが自動採番する記録ID
    id: int
    # counter_id: 紐づくカウンターのID
    counter_id: int
    # date: 実行日（"YYYY-MM-DD"形式）
    date: str
    # created_at: 作成日時
    created_at: str

    class Config:
        """SQLAlchemyモデルからの変換を許可"""
        from_attributes = True
```

### 実行・確認

```bash
# スキーマが正しく読み込めることを確認
$ python -c "from app.schemas import CounterCreate, CounterResponse, RecordCreate, RecordResponse; print('OK')"
OK
```

---

## 2-2. CRUD関数の実装

### 作成ファイル: `backend/app/crud.py`

#### このファイルの役割
データベース操作のビジネスロジックを集約する。ルーター（API層）から呼び出され、日付バリデーションや重複チェックなどのルールを実装する。

#### コード

```python
"""CRUD操作 — カウンターと記録のデータベース操作ロジック"""

# date: 日付操作用。今日の日付取得や日付の差分計算に使用
from datetime import date, timedelta
# HTTPException: エラーレスポンスを返すための例外クラス
from fastapi import HTTPException
# Session: SQLAlchemyのDBセッション型（型ヒント用）
from sqlalchemy.orm import Session
# IntegrityError: DB制約違反（ユニーク制約など）時の例外
from sqlalchemy.exc import IntegrityError

# テーブルモデル
from .models import Counter, Record
# リクエストスキーマ
from .schemas import CounterCreate, RecordCreate


# ============================
# カウンター操作
# ============================

def get_counters(db: Session) -> list[Counter]:
    """全カウンターを取得し、各カウンターにtoday_done属性を付与する。

    today_done: 今日の日付の記録が存在すればTrue、なければFalse。
    sort_order昇順 → id昇順で返す。
    """
    # 全カウンターを取得（sort_order → id の順でソート）
    counters = db.query(Counter).order_by(Counter.sort_order, Counter.id).all()
    # 今日の日付を "YYYY-MM-DD" 形式の文字列で取得
    today = date.today().isoformat()
    for counter in counters:
        # 今日の記録が存在するかチェック
        # any()は1件でもTrueがあればTrueを返す（全レコードをスキャンせず効率的）
        counter.today_done = any(r.date == today for r in counter.records)
    return counters


def create_counter(db: Session, data: CounterCreate) -> Counter:
    """新しいカウンターを作成してDBに保存する。"""
    # スキーマのデータからCounterモデルのインスタンスを作成
    counter = Counter(name=data.name)
    # DBセッションに追加
    db.add(counter)
    # コミットしてDBに保存
    db.commit()
    # DB側で設定された値（id, created_at）を読み込み直す
    db.refresh(counter)
    # today_doneを付与（新規作成時は常にFalse）
    counter.today_done = False
    return counter


def delete_counter(db: Session, counter_id: int) -> None:
    """指定IDのカウンターを削除する。存在しない場合は404エラー。

    CASCADE設定により、関連するRecordも自動削除される。
    """
    # 指定IDのカウンターを取得
    counter = db.query(Counter).filter(Counter.id == counter_id).first()
    if not counter:
        # 存在しない場合は404エラーを返す
        raise HTTPException(status_code=404, detail="カウンターが見つかりません")
    # 削除してコミット
    db.delete(counter)
    db.commit()


# ============================
# 記録操作
# ============================

def _validate_date(date_str: str) -> date:
    """日付文字列のバリデーション。以下のルールを適用する:

    1. "YYYY-MM-DD" 形式であること（不正な形式 → 400）
    2. 未来の日付でないこと（未来日 → 400）
    3. 3日前より新しいこと（4日以上前 → 400）

    戻り値: バリデーション済みのdateオブジェクト
    """
    # 形式チェック: "YYYY-MM-DD" 形式でなければ400エラー
    try:
        parsed = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"日付の形式が不正です: {date_str}（YYYY-MM-DD形式で指定してください）"
        )

    today = date.today()

    # 未来日チェック
    if parsed > today:
        raise HTTPException(
            status_code=400,
            detail=f"未来の日付は記録できません: {date_str}"
        )

    # 3日前チェック: today - 3日 = 編集可能な最古の日付
    oldest_allowed = today - timedelta(days=3)
    if parsed < oldest_allowed:
        raise HTTPException(
            status_code=400,
            detail=f"3日前より古い日付は記録できません: {date_str}（{oldest_allowed} 以降を指定してください）"
        )

    return parsed


def get_records_by_month(db: Session, counter_id: int, year: int, month: int) -> list[Record]:
    """指定カウンターの指定年月の記録を取得する。

    dateカラムは "YYYY-MM-DD" 形式のテキストなので、
    LIKE句で "2026-02-%" のようにフィルタする。
    """
    # 月を2桁ゼロ埋めで文字列化（例: 2 → "02"）
    month_str = f"{year}-{month:02d}"
    # LIKE句で前方一致検索（"2026-02-%" にマッチする全レコード）
    records = (
        db.query(Record)
        .filter(Record.counter_id == counter_id)
        .filter(Record.date.like(f"{month_str}-%"))
        .order_by(Record.date)
        .all()
    )
    return records


def create_record(db: Session, counter_id: int, data: RecordCreate) -> Record:
    """実行記録を作成する。日付バリデーション + 重複チェックを行う。

    エラーケース:
    - 日付形式不正 → 400
    - 未来日 → 400
    - 3日前超 → 400
    - 同日重複 → 409 Conflict
    - カウンター不存在 → 404
    """
    # カウンターの存在確認
    counter = db.query(Counter).filter(Counter.id == counter_id).first()
    if not counter:
        raise HTTPException(status_code=404, detail="カウンターが見つかりません")

    # 日付バリデーション（形式・未来日・3日前チェック）
    _validate_date(data.date)

    # 記録を作成してDBに保存
    record = Record(counter_id=counter_id, date=data.date)
    db.add(record)
    try:
        # コミット時にUniqueConstraint違反があればIntegrityErrorが発生
        db.commit()
    except IntegrityError:
        # ロールバックしてセッションをクリーンな状態に戻す
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"この日付はすでに記録済みです: {data.date}"
        )
    db.refresh(record)
    return record


def delete_record(db: Session, counter_id: int, date_str: str) -> None:
    """指定カウンターの指定日付の記録を削除する。

    存在しない場合は404エラー。
    """
    # counter_idとdateの組み合わせで検索
    record = (
        db.query(Record)
        .filter(Record.counter_id == counter_id, Record.date == date_str)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="記録が見つかりません")
    db.delete(record)
    db.commit()
```

### 実行・確認

```bash
# CRUD関数が正しく読み込めることを確認
$ python -c "from app.crud import get_counters, create_counter, create_record; print('OK')"
OK
```

---

## 2-3. ルーターの初期化

### 作成ファイル: `backend/app/routers/__init__.py`

#### このファイルの役割
`routers` ディレクトリをPythonパッケージとして認識させる。

#### コード

```python
# 空ファイル — Pythonパッケージとして認識させるために必要
```

### 実行・確認

```bash
$ mkdir -p app/routers
$ touch app/routers/__init__.py
```

---

## 2-4. カウンター API ルーター

### 作成ファイル: `backend/app/routers/counters.py`

#### このファイルの役割
カウンターに関するAPIエンドポイント（一覧・作成・削除）を定義する。

#### コード

```python
"""カウンターAPIルーター — 一覧取得・作成・削除"""

# APIRouter: FastAPIのルーター。エンドポイントをグループ化する
# Depends: Dependency Injection。get_dbからDBセッションを受け取る
from fastapi import APIRouter, Depends
# Response: HTTPレスポンスオブジェクト。ステータスコードを直接指定するために使用
from fastapi.responses import Response
# Session: SQLAlchemyのセッション型（型ヒント用）
from sqlalchemy.orm import Session

# DB接続のDI関数
from ..database import get_db
# CRUD関数
from .. import crud
# レスポンス/リクエストスキーマ
from ..schemas import CounterCreate, CounterResponse

# ルーターを作成
# prefix="/api/counters": このルーター内の全パスに /api/counters が付く
# tags=["counters"]: Swagger UIでのグループ名
router = APIRouter(prefix="/api/counters", tags=["counters"])


@router.get("", response_model=list[CounterResponse])
def list_counters(db: Session = Depends(get_db)):
    """カウンター一覧を取得する。
    各カウンターにはtoday_done（今日実行済みかどうか）が付与される。

    レスポンス例:
    [
        {"id": 1, "name": "筋トレ", "created_at": "2026-...", "sort_order": 0, "today_done": true},
        {"id": 2, "name": "読書", "created_at": "2026-...", "sort_order": 0, "today_done": false}
    ]
    """
    return crud.get_counters(db)


@router.post("", response_model=CounterResponse, status_code=201)
def create_counter(data: CounterCreate, db: Session = Depends(get_db)):
    """新しいカウンターを作成する。

    リクエストボディ: {"name": "筋トレ"}
    レスポンス: 作成されたカウンター（status: 201 Created）
    """
    return crud.create_counter(db, data)


@router.delete("/{counter_id}", status_code=204)
def delete_counter(counter_id: int, db: Session = Depends(get_db)):
    """カウンターを削除する。関連する記録も全て削除される（CASCADE）。

    レスポンス: 204 No Content（ボディなし）
    存在しないIDの場合: 404 Not Found
    """
    crud.delete_counter(db, counter_id)
    # 204 No Contentはボディを返さない
    return Response(status_code=204)
```

---

## 2-5. 記録 API ルーター

### 作成ファイル: `backend/app/routers/records.py`

#### このファイルの役割
実行記録に関するAPIエンドポイント（月別取得・作成・削除）を定義する。

#### コード

```python
"""記録APIルーター — 月別取得・作成・削除"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud
from ..schemas import RecordCreate, RecordResponse

# ルーターを作成
# prefix="/api/counters/{counter_id}/records": RESTfulなネスト構造
# カウンターに紐づく記録、というリソース階層を表現
router = APIRouter(prefix="/api/counters/{counter_id}/records", tags=["records"])


@router.get("", response_model=list[RecordResponse])
def list_records(
    counter_id: int,
    year: int = Query(..., description="年（例: 2026）"),
    month: int = Query(..., description="月（1-12）"),
    db: Session = Depends(get_db),
):
    """指定カウンターの指定年月の記録を取得する。

    クエリパラメータ:
        year: 年（必須）
        month: 月（必須、1-12）

    リクエスト例: GET /api/counters/1/records?year=2026&month=2
    レスポンス例:
    [
        {"id": 1, "counter_id": 1, "date": "2026-02-01", "created_at": "..."},
        {"id": 2, "counter_id": 1, "date": "2026-02-15", "created_at": "..."}
    ]
    """
    return crud.get_records_by_month(db, counter_id, year, month)


@router.post("", response_model=RecordResponse, status_code=201)
def create_record(
    counter_id: int,
    data: RecordCreate,
    db: Session = Depends(get_db),
):
    """実行記録を作成する。

    リクエストボディ: {"date": "2026-02-23"}

    バリデーション:
    - 未来日 → 400 Bad Request
    - 3日前超 → 400 Bad Request
    - 重複 → 409 Conflict
    """
    return crud.create_record(db, counter_id, data)


@router.delete("/{date}", status_code=204)
def delete_record(
    counter_id: int,
    date: str,
    db: Session = Depends(get_db),
):
    """指定日付の記録を削除する。

    パスパラメータ:
        date: "YYYY-MM-DD" 形式の日付

    リクエスト例: DELETE /api/counters/1/records/2026-02-23
    レスポンス: 204 No Content
    """
    crud.delete_record(db, counter_id, date)
    return Response(status_code=204)
```

---

## 2-6. main.py の更新（ルーター登録 + CORS設定）

### 更新ファイル: `backend/app/main.py`

#### 変更内容
ルーターの登録とCORS（Cross-Origin Resource Sharing）ミドルウェアを追加する。

#### コード（全体を差し替え）

```python
"""FastAPIアプリケーションのエントリポイント"""

# FastAPI: Webアプリケーションフレームワークのメインクラス
from fastapi import FastAPI
# CORSMiddleware: 異なるオリジン（ドメイン）からのアクセスを許可するミドルウェア
from fastapi.middleware.cors import CORSMiddleware

# DB接続エンジンとBaseクラス
from .database import engine, Base
# ルーター（APIエンドポイントの定義）
from .routers import counters, records

# アプリケーション起動時にテーブルを自動作成
Base.metadata.create_all(bind=engine)

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI(title="Anything Counter", version="0.1.0")

# CORS設定: フロントエンド（Vite devサーバー）からのアクセスを許可
# フロントエンドとバックエンドが別ポートで動くため、CORSの設定が必要
app.add_middleware(
    CORSMiddleware,
    # 許可するオリジン（フロントエンドのURL）
    allow_origins=["http://localhost:5173"],
    # Cookieの送信を許可（将来の認証用、現時点では不要だが設定しておく）
    allow_credentials=True,
    # 全てのHTTPメソッドを許可（GET, POST, DELETE, etc.）
    allow_methods=["*"],
    # 全てのHTTPヘッダーを許可
    allow_headers=["*"],
)

# ルーターを登録（各ルーターのエンドポイントがアプリに追加される）
app.include_router(counters.router)
app.include_router(records.router)


@app.get("/health")
def health_check():
    """ヘルスチェック用エンドポイント。サーバーが正常に動作しているか確認する"""
    return {"status": "ok"}
```

---

## 2-7. CRUD テストの作成

### 作成ファイル: `backend/tests/test_crud.py`

#### このファイルの役割
CRUD関数のビジネスロジック（日付バリデーション、重複チェックなど）をテストする。

#### コード

```python
"""CRUD関数のテスト — ビジネスロジックの検証"""

# date, timedelta: テスト用の日付計算
from datetime import date, timedelta
# pytest: テストフレームワーク。例外テスト用のraisesを使う
import pytest
# HTTPException: FastAPIのエラーレスポンス例外
from fastapi import HTTPException

# テスト対象のCRUD関数
from app.crud import (
    create_counter,
    get_counters,
    delete_counter,
    create_record,
    get_records_by_month,
    delete_record,
)
# リクエストスキーマ
from app.schemas import CounterCreate, RecordCreate


class TestCounterCrud:
    """カウンターCRUD関数のテスト"""

    def test_カウンターを作成できる(self, db):
        """create_counterでカウンターが作成され、DBに保存されることを確認"""
        counter = create_counter(db, CounterCreate(name="筋トレ"))
        assert counter.id is not None
        assert counter.name == "筋トレ"
        assert counter.today_done is False

    def test_カウンター一覧を取得できる(self, db):
        """get_countersで全カウンターが取得できることを確認"""
        create_counter(db, CounterCreate(name="筋トレ"))
        create_counter(db, CounterCreate(name="読書"))
        counters = get_counters(db)
        assert len(counters) == 2

    def test_カウンターを削除できる(self, db):
        """delete_counterでカウンターが削除されることを確認"""
        counter = create_counter(db, CounterCreate(name="筋トレ"))
        delete_counter(db, counter.id)
        counters = get_counters(db)
        assert len(counters) == 0

    def test_存在しないカウンターの削除で404(self, db):
        """存在しないIDを指定するとHTTPException(404)が発生することを確認"""
        with pytest.raises(HTTPException) as exc_info:
            delete_counter(db, 999)
        assert exc_info.value.status_code == 404


class TestRecordCrud:
    """記録CRUD関数のテスト"""

    def test_記録を作成できる(self, db):
        """create_recordで記録が作成されることを確認"""
        counter = create_counter(db, CounterCreate(name="筋トレ"))
        today = date.today().isoformat()
        record = create_record(db, counter.id, RecordCreate(date=today))
        assert record.counter_id == counter.id
        assert record.date == today

    def test_未来日の記録は400エラー(self, db):
        """未来の日付を指定するとHTTPException(400)が発生することを確認"""
        counter = create_counter(db, CounterCreate(name="筋トレ"))
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        with pytest.raises(HTTPException) as exc_info:
            create_record(db, counter.id, RecordCreate(date=tomorrow))
        assert exc_info.value.status_code == 400

    def test_4日前の記録は400エラー(self, db):
        """4日以上前の日付を指定するとHTTPException(400)が発生することを確認"""
        counter = create_counter(db, CounterCreate(name="筋トレ"))
        four_days_ago = (date.today() - timedelta(days=4)).isoformat()
        with pytest.raises(HTTPException) as exc_info:
            create_record(db, counter.id, RecordCreate(date=four_days_ago))
        assert exc_info.value.status_code == 400

    def test_3日前の記録は作成できる(self, db):
        """3日前の日付は許可されることを確認（境界値テスト）"""
        counter = create_counter(db, CounterCreate(name="筋トレ"))
        three_days_ago = (date.today() - timedelta(days=3)).isoformat()
        record = create_record(db, counter.id, RecordCreate(date=three_days_ago))
        assert record.date == three_days_ago

    def test_同日重複は409エラー(self, db):
        """同じカウンター・同じ日付で2回記録するとHTTPException(409)が発生することを確認"""
        counter = create_counter(db, CounterCreate(name="筋トレ"))
        today = date.today().isoformat()
        create_record(db, counter.id, RecordCreate(date=today))
        with pytest.raises(HTTPException) as exc_info:
            create_record(db, counter.id, RecordCreate(date=today))
        assert exc_info.value.status_code == 409

    def test_月別記録を取得できる(self, db):
        """get_records_by_monthで指定年月の記録のみ取得できることを確認"""
        counter = create_counter(db, CounterCreate(name="筋トレ"))
        today = date.today()
        # 今月の記録を作成
        create_record(db, counter.id, RecordCreate(date=today.isoformat()))
        records = get_records_by_month(db, counter.id, today.year, today.month)
        assert len(records) == 1
        assert records[0].date == today.isoformat()

    def test_記録を削除できる(self, db):
        """delete_recordで記録が削除されることを確認"""
        counter = create_counter(db, CounterCreate(name="筋トレ"))
        today = date.today().isoformat()
        create_record(db, counter.id, RecordCreate(date=today))
        delete_record(db, counter.id, today)
        records = get_records_by_month(db, counter.id, date.today().year, date.today().month)
        assert len(records) == 0

    def test_存在しない記録の削除で404(self, db):
        """存在しない記録を削除しようとするとHTTPException(404)が発生することを確認"""
        counter = create_counter(db, CounterCreate(name="筋トレ"))
        with pytest.raises(HTTPException) as exc_info:
            delete_record(db, counter.id, "2026-01-01")
        assert exc_info.value.status_code == 404
```

---

## 2-8. カウンター API テストの作成

### 作成ファイル: `backend/tests/test_counters.py`

#### このファイルの役割
カウンター API エンドポイントの統合テスト。HTTPリクエスト経由でステータスコードとレスポンスボディを検証する。

#### コード

```python
"""カウンターAPIのテスト — エンドポイントの統合テスト"""


class TestCounterAPI:
    """カウンターAPIの統合テスト"""

    def test_空のカウンター一覧を取得(self, client):
        """初期状態ではカウンター一覧が空であることを確認"""
        response = client.get("/api/counters")
        assert response.status_code == 200
        assert response.json() == []

    def test_カウンターを作成(self, client):
        """POST /api/counters でカウンターが作成されることを確認"""
        response = client.post("/api/counters", json={"name": "筋トレ"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "筋トレ"
        assert data["id"] is not None
        assert data["today_done"] is False

    def test_カウンター一覧に作成済みが含まれる(self, client):
        """作成したカウンターが一覧に含まれることを確認"""
        client.post("/api/counters", json={"name": "筋トレ"})
        response = client.get("/api/counters")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "筋トレ"

    def test_カウンターを削除(self, client):
        """DELETE /api/counters/{id} でカウンターが削除されることを確認"""
        # まず作成
        create_response = client.post("/api/counters", json={"name": "筋トレ"})
        counter_id = create_response.json()["id"]
        # 削除
        response = client.delete(f"/api/counters/{counter_id}")
        assert response.status_code == 204
        # 一覧が空になったことを確認
        list_response = client.get("/api/counters")
        assert list_response.json() == []

    def test_存在しないカウンターの削除で404(self, client):
        """存在しないIDを削除しようとすると404が返ることを確認"""
        response = client.delete("/api/counters/999")
        assert response.status_code == 404
```

---

## 2-9. 記録 API テストの作成

### 作成ファイル: `backend/tests/test_records.py`

#### このファイルの役割
記録 API エンドポイントの統合テスト。日付バリデーションのHTTPレスポンスも検証する。

#### コード

```python
"""記録APIのテスト — エンドポイントの統合テスト"""

# テスト用の日付計算
from datetime import date, timedelta


class TestRecordAPI:
    """記録APIの統合テスト"""

    def _create_counter(self, client) -> int:
        """テスト用ヘルパー: カウンターを作成してIDを返す"""
        response = client.post("/api/counters", json={"name": "筋トレ"})
        return response.json()["id"]

    def test_記録を作成(self, client):
        """POST /api/counters/{id}/records で記録が作成されることを確認"""
        counter_id = self._create_counter(client)
        today = date.today().isoformat()
        response = client.post(
            f"/api/counters/{counter_id}/records",
            json={"date": today},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["counter_id"] == counter_id
        assert data["date"] == today

    def test_月別記録を取得(self, client):
        """GET /api/counters/{id}/records?year=&month= で月別記録を取得できることを確認"""
        counter_id = self._create_counter(client)
        today = date.today()
        # 記録を作成
        client.post(
            f"/api/counters/{counter_id}/records",
            json={"date": today.isoformat()},
        )
        # 月別で取得
        response = client.get(
            f"/api/counters/{counter_id}/records",
            params={"year": today.year, "month": today.month},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_未来日の記録作成で400(self, client):
        """未来の日付で記録を作ろうとすると400が返ることを確認"""
        counter_id = self._create_counter(client)
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        response = client.post(
            f"/api/counters/{counter_id}/records",
            json={"date": tomorrow},
        )
        assert response.status_code == 400

    def test_4日前の記録作成で400(self, client):
        """4日以上前の日付で記録を作ろうとすると400が返ることを確認"""
        counter_id = self._create_counter(client)
        four_days_ago = (date.today() - timedelta(days=4)).isoformat()
        response = client.post(
            f"/api/counters/{counter_id}/records",
            json={"date": four_days_ago},
        )
        assert response.status_code == 400

    def test_同日重複で409(self, client):
        """同じ日に2回記録しようとすると409が返ることを確認"""
        counter_id = self._create_counter(client)
        today = date.today().isoformat()
        client.post(
            f"/api/counters/{counter_id}/records",
            json={"date": today},
        )
        response = client.post(
            f"/api/counters/{counter_id}/records",
            json={"date": today},
        )
        assert response.status_code == 409

    def test_記録を削除(self, client):
        """DELETE /api/counters/{id}/records/{date} で記録が削除されることを確認"""
        counter_id = self._create_counter(client)
        today = date.today().isoformat()
        client.post(
            f"/api/counters/{counter_id}/records",
            json={"date": today},
        )
        response = client.delete(
            f"/api/counters/{counter_id}/records/{today}"
        )
        assert response.status_code == 204

    def test_記録作成後にtoday_doneがtrueになる(self, client):
        """記録作成後、カウンター一覧のtoday_doneがtrueになることを確認"""
        counter_id = self._create_counter(client)
        today = date.today().isoformat()
        # 記録を作成
        client.post(
            f"/api/counters/{counter_id}/records",
            json={"date": today},
        )
        # カウンター一覧を確認
        response = client.get("/api/counters")
        data = response.json()
        assert data[0]["today_done"] is True
```

---

## テスト実行

```bash
# backendディレクトリで実行
$ cd backend
$ pytest -v

# 期待される出力:
tests/test_counters.py::TestCounterAPI::test_空のカウンター一覧を取得 PASSED
tests/test_counters.py::TestCounterAPI::test_カウンターを作成 PASSED
tests/test_counters.py::TestCounterAPI::test_カウンター一覧に作成済みが含まれる PASSED
tests/test_counters.py::TestCounterAPI::test_カウンターを削除 PASSED
tests/test_counters.py::TestCounterAPI::test_存在しないカウンターの削除で404 PASSED
tests/test_crud.py::TestCounterCrud::test_カウンターを作成できる PASSED
tests/test_crud.py::TestCounterCrud::test_カウンター一覧を取得できる PASSED
tests/test_crud.py::TestCounterCrud::test_カウンターを削除できる PASSED
tests/test_crud.py::TestCounterCrud::test_存在しないカウンターの削除で404 PASSED
tests/test_crud.py::TestRecordCrud::test_記録を作成できる PASSED
tests/test_crud.py::TestRecordCrud::test_未来日の記録は400エラー PASSED
tests/test_crud.py::TestRecordCrud::test_4日前の記録は400エラー PASSED
tests/test_crud.py::TestRecordCrud::test_3日前の記録は作成できる PASSED
tests/test_crud.py::TestRecordCrud::test_同日重複は409エラー PASSED
tests/test_crud.py::TestRecordCrud::test_月別記録を取得できる PASSED
tests/test_crud.py::TestRecordCrud::test_記録を削除できる PASSED
tests/test_crud.py::TestRecordCrud::test_存在しない記録の削除で404 PASSED
tests/test_health.py::test_ヘルスチェックが正常に動作する PASSED
tests/test_models.py::TestCounterModel::test_カウンターを作成できる PASSED
tests/test_models.py::TestCounterModel::test_複数カウンターを作成できる PASSED
tests/test_models.py::TestRecordModel::test_実行記録を作成できる PASSED
tests/test_models.py::TestRecordModel::test_カウンター削除時に記録も削除される PASSED
tests/test_models.py::TestRecordModel::test_同じ日に同じカウンターで重複記録できない PASSED
tests/test_records.py::TestRecordAPI::test_記録を作成 PASSED
tests/test_records.py::TestRecordAPI::test_月別記録を取得 PASSED
tests/test_records.py::TestRecordAPI::test_未来日の記録作成で400 PASSED
tests/test_records.py::TestRecordAPI::test_4日前の記録作成で400 PASSED
tests/test_records.py::TestRecordAPI::test_同日重複で409 PASSED
tests/test_records.py::TestRecordAPI::test_記録を削除 PASSED
tests/test_records.py::TestRecordAPI::test_記録作成後にtoday_doneがtrueになる PASSED

========================= 30 passed =========================
```

---

## curl での手動テスト

サーバーを起動してから、別ターミナルで以下を実行する。

```bash
# サーバー起動（別ターミナル）
$ uvicorn app.main:app --reload --port 8000

# --- カウンター操作 ---

# カウンター作成
$ curl -X POST http://localhost:8000/api/counters \
  -H "Content-Type: application/json" \
  -d '{"name": "筋トレ"}'
# → {"id":1,"name":"筋トレ","created_at":"...","sort_order":0,"today_done":false}

# カウンター一覧
$ curl http://localhost:8000/api/counters
# → [{"id":1,"name":"筋トレ","created_at":"...","sort_order":0,"today_done":false}]

# --- 記録操作 ---

# 今日の記録を作成（日付は実行日に合わせて変更）
$ curl -X POST http://localhost:8000/api/counters/1/records \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-03-03"}'
# → {"id":1,"counter_id":1,"date":"2026-03-03","created_at":"..."}

# 月別記録を取得
$ curl "http://localhost:8000/api/counters/1/records?year=2026&month=3"
# → [{"id":1,"counter_id":1,"date":"2026-03-03","created_at":"..."}]

# today_doneがtrueに変わったことを確認
$ curl http://localhost:8000/api/counters
# → [{"id":1,"name":"筋トレ","created_at":"...","sort_order":0,"today_done":true}]

# --- エラーケース ---

# 未来日（400エラー）
$ curl -X POST http://localhost:8000/api/counters/1/records \
  -H "Content-Type: application/json" \
  -d '{"date": "2099-01-01"}'
# → {"detail":"未来の日付は記録できません: 2099-01-01"}

# 同日重複（409エラー）
$ curl -X POST http://localhost:8000/api/counters/1/records \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-03-03"}'
# → {"detail":"この日付はすでに記録済みです: 2026-03-03"}

# --- 削除 ---

# 記録削除
$ curl -X DELETE http://localhost:8000/api/counters/1/records/2026-03-03
# → (204 No Content、ボディなし)

# カウンター削除
$ curl -X DELETE http://localhost:8000/api/counters/1
# → (204 No Content、ボディなし)
```

---

## このステップのディレクトリ構造

```
backend/
├── requirements.txt
├── requirements-dev.txt
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── main.py               # ← 更新（CORS + ルーター登録）
│   ├── schemas.py             # ← 新規
│   ├── crud.py                # ← 新規
│   └── routers/
│       ├── __init__.py        # ← 新規
│       ├── counters.py        # ← 新規
│       └── records.py         # ← 新規
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_models.py
    ├── test_health.py
    ├── test_crud.py           # ← 新規
    ├── test_counters.py       # ← 新規
    └── test_records.py        # ← 新規
```

---

## このステップの完了チェックリスト

- [ ] `pytest -v` で30件全てのテストがパスする
- [ ] `curl` でカウンターの作成・一覧・削除ができる
- [ ] `curl` で記録の作成・月別取得・削除ができる
- [ ] 未来日の記録作成が400で拒否される
- [ ] 4日前の記録作成が400で拒否される
- [ ] 同日重複の記録作成が409で拒否される
- [ ] Swagger UI (`http://localhost:8000/docs`) で全エンドポイントが表示される
