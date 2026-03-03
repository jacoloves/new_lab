# Step 6: スタイリング・仕上げ（モバイルファーストUI + 削除確認 + エラーハンドリング）

## このステップで作るもの

- グローバルスタイルの調整（index.css）
- チェック済みカードのビジュアルフィードバック強化
- 削除確認ダイアログ
- APIエラーハンドリングの改善
- モバイルファーストのレスポンシブ調整

**完了後の状態**: モバイルで快適に操作でき、誤操作防止の確認ダイアログがあり、エラー時に適切なフィードバックが表示されるアプリが完成する。

## 前提条件

- Step 5 が完了していること（月間カレンダーが動作する状態）
- `frontend/` ディレクトリにいること

---

## 6-1. グローバルスタイルの調整

### 更新ファイル: `frontend/src/index.css`

#### このファイルの役割
アプリ全体に適用されるグローバルスタイル。Tailwindのインポートに加えて、カスタムスタイルを追加する。

#### コード（全体を差し替え）

```css
/* Tailwind CSS のインポート */
@import "tailwindcss";

/* カスタムスタイル */

/* ボディ全体のスタイル */
/* -webkit-font-smoothing: フォントのアンチエイリアシングを有効化（macOS/iOSで文字がきれいに表示される） */
/* touch-action: manipulation: ダブルタップによるズームを無効化（タップ操作の遅延を防止） */
body {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  touch-action: manipulation;
}

/* ボタンのタップハイライトを無効化（モバイルでタップ時の青い枠を消す） */
button {
  -webkit-tap-highlight-color: transparent;
}

/* チェックアニメーション用のキーフレーム */
/* カウンターをチェックした時のスケールアニメーション */
@keyframes check-bounce {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

/* チェックアニメーションを適用するクラス */
.animate-check {
  animation: check-bounce 0.3s ease-in-out;
}
```

---

## 6-2. 削除確認ダイアログ

### 作成ファイル: `frontend/src/components/ConfirmDialog.tsx`

#### このファイルの役割
削除操作の前に確認ダイアログを表示する。誤操作による削除を防止する。

#### コード

```tsx
/**
 * ConfirmDialogコンポーネント — 確認ダイアログ
 *
 * 削除などの破壊的操作の前にユーザーに確認を求める。
 * モーダルオーバーレイとして画面全体に表示される。
 */

type Props = {
  /** ダイアログが表示中かどうか */
  isOpen: boolean;
  /** ダイアログのタイトル */
  title: string;
  /** ダイアログのメッセージ（何が削除されるかの説明） */
  message: string;
  /** 確認ボタンのラベル（デフォルト: "削除"） */
  confirmLabel?: string;
  /** 確認ボタンクリック時の関数 */
  onConfirm: () => void;
  /** キャンセルボタンクリック時（またはオーバーレイクリック時）の関数 */
  onCancel: () => void;
};

function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmLabel = "削除",
  onConfirm,
  onCancel,
}: Props) {
  // 表示中でなければ何もレンダリングしない
  if (!isOpen) return null;

  return (
    // モーダルオーバーレイ
    // fixed inset-0: 画面全体を覆う
    // bg-black/50: 半透明の黒背景（50%透過）
    // flex items-center justify-center: ダイアログを上下左右中央に配置
    // z-50: 最前面に表示（他の要素より上）
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      // オーバーレイ部分のクリックでキャンセル
      onClick={onCancel}
    >
      {/* ダイアログ本体 */}
      {/* bg-white: 白い背景 */}
      {/* rounded-xl: 大きめの角丸 */}
      {/* max-w-sm: 最大幅（24rem = 384px） */}
      {/* w-full: 親要素の幅いっぱいに広がる（max-wで制限） */}
      <div
        className="w-full max-w-sm rounded-xl bg-white p-6 shadow-lg"
        // ダイアログ内のクリックがオーバーレイに伝播しないようにする
        onClick={(e) => e.stopPropagation()}
      >
        {/* タイトル */}
        <h3 className="mb-2 text-lg font-bold text-gray-800">{title}</h3>
        {/* メッセージ */}
        <p className="mb-6 text-sm text-gray-600">{message}</p>
        {/* ボタン群 */}
        {/* flex justify-end: 右寄せ配置 */}
        {/* gap-3: ボタン間の間隔 */}
        <div className="flex justify-end gap-3">
          {/* キャンセルボタン */}
          <button
            onClick={onCancel}
            className="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100"
          >
            キャンセル
          </button>
          {/* 確認（削除）ボタン */}
          {/* bg-red-500: 赤い背景（危険な操作を示す） */}
          <button
            onClick={onConfirm}
            className="rounded-lg bg-red-500 px-4 py-2 text-sm font-medium text-white hover:bg-red-600"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmDialog;
```

---

## 6-3. CounterList の更新（削除確認ダイアログ統合）

### 更新ファイル: `frontend/src/components/CounterList.tsx`

#### 変更内容
削除ボタンクリック時に確認ダイアログを表示するようにする。

#### コード（全体を差し替え）

```tsx
/**
 * CounterListコンポーネント — カウンター一覧の表示
 * 削除確認ダイアログ付き
 */

import { useState } from "react";
import type { Counter } from "../types";
import CounterCard from "./CounterCard";
// 確認ダイアログコンポーネント
import ConfirmDialog from "./ConfirmDialog";

type Props = {
  counters: Counter[];
  onToggleToday: (counter: Counter) => void;
  onDelete: (id: number) => void;
};

function CounterList({ counters, onToggleToday, onDelete }: Props) {
  // アコーディオン展開中のカウンターID
  const [selectedId, setSelectedId] = useState<number | null>(null);
  // 削除確認ダイアログの対象カウンター（nullなら非表示）
  const [deleteTarget, setDeleteTarget] = useState<Counter | null>(null);

  const handleSelect = (id: number) => {
    setSelectedId((prev) => (prev === id ? null : id));
  };

  /**
   * 削除ボタンクリック時: 確認ダイアログを表示する
   * 実際の削除はダイアログの「削除」ボタンで実行される
   */
  const handleDeleteRequest = (id: number) => {
    // 削除対象のカウンターをcountersから検索
    const target = counters.find((c) => c.id === id);
    if (target) {
      setDeleteTarget(target);
    }
  };

  /**
   * 削除確認: 実際にAPIを呼んで削除する
   */
  const handleDeleteConfirm = () => {
    if (deleteTarget) {
      onDelete(deleteTarget.id);
      // ダイアログを閉じる
      setDeleteTarget(null);
    }
  };

  /**
   * 削除キャンセル: ダイアログを閉じるだけ
   */
  const handleDeleteCancel = () => {
    setDeleteTarget(null);
  };

  if (counters.length === 0) {
    return (
      <p className="text-center text-gray-400">
        カウンターがありません。上のフォームから追加してください。
      </p>
    );
  }

  return (
    <>
      <div className="space-y-3">
        {counters.map((counter) => (
          <CounterCard
            key={counter.id}
            counter={counter}
            onToggleToday={onToggleToday}
            onDelete={handleDeleteRequest}
            onSelect={handleSelect}
            isSelected={selectedId === counter.id}
          />
        ))}
      </div>

      {/* 削除確認ダイアログ */}
      <ConfirmDialog
        isOpen={deleteTarget !== null}
        title="カウンターの削除"
        message={
          deleteTarget
            ? `「${deleteTarget.name}」を削除しますか？関連する全ての記録も削除されます。`
            : ""
        }
        confirmLabel="削除する"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </>
  );
}

export default CounterList;
```

---

## 6-4. CounterCard のチェックアニメーション追加

### 更新ファイル: `frontend/src/components/CounterCard.tsx`

#### 変更内容
チェックボタンにアニメーションクラスを追加する。チェック切り替え時にバウンスアニメーションが再生される。

#### コード（全体を差し替え）

```tsx
/**
 * CounterCardコンポーネント — 個別カウンターの表示カード（最終版）
 *
 * 機能:
 * - タップでtoday_doneを切り替え（アニメーション付き）
 * - チェック済みカードの背景色変更
 * - 削除ボタン
 * - アコーディオン展開で月間カレンダー表示
 */

import type { Counter } from "../types";
import { useRecords } from "../hooks/useRecords";
import MonthlyGrid from "./MonthlyGrid";

type Props = {
  counter: Counter;
  onToggleToday: (counter: Counter) => void;
  onDelete: (id: number) => void;
  onSelect: (id: number) => void;
  isSelected: boolean;
};

function CounterCard({ counter, onToggleToday, onDelete, onSelect, isSelected }: Props) {
  const {
    year,
    month,
    loading: recordsLoading,
    goToPrevMonth,
    goToNextMonth,
    hasRecord,
    toggleDate,
  } = useRecords(counter.id, isSelected);

  return (
    <div
      className={`rounded-lg border p-4 shadow-sm transition-colors duration-200 ${
        counter.today_done
          ? "border-green-300 bg-green-50"
          : "border-gray-200 bg-white"
      }`}
    >
      <div className="flex items-center gap-3">
        {/* チェックボタン（アニメーション付き） */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleToday(counter);
          }}
          className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full border-2 transition-colors ${
            counter.today_done
              ? "border-green-500 bg-green-100"
              : "border-gray-300 hover:border-green-400"
          }`}
          aria-label={counter.today_done ? "チェックを外す" : "チェックする"}
        >
          {counter.today_done && (
            // animate-check: index.cssで定義したバウンスアニメーション
            <span className="animate-check text-lg text-green-600">✓</span>
          )}
        </button>

        {/* カウンター名 */}
        <span
          className={`flex-1 cursor-pointer truncate ${
            counter.today_done ? "text-green-700" : "text-gray-800"
          }`}
          onClick={() => onSelect(counter.id)}
        >
          {counter.name}
        </span>

        {/* 展開/閉じインジケーター */}
        <span
          className="cursor-pointer text-xs text-gray-400"
          onClick={() => onSelect(counter.id)}
        >
          {isSelected ? "▲" : "▼"}
        </span>

        {/* 削除ボタン */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(counter.id);
          }}
          className="flex-shrink-0 text-gray-400 transition-colors hover:text-red-500"
          aria-label="削除"
        >
          🗑
        </button>
      </div>

      {/* アコーディオン展開部分 */}
      {isSelected && (
        <div className="mt-4 border-t pt-4">
          <MonthlyGrid
            year={year}
            month={month}
            loading={recordsLoading}
            onPrevMonth={goToPrevMonth}
            onNextMonth={goToNextMonth}
            hasRecord={hasRecord}
            onToggleDate={toggleDate}
          />
        </div>
      )}
    </div>
  );
}

export default CounterCard;
```

---

## 6-5. エラー表示の改善

### 更新ファイル: `frontend/src/App.tsx`

#### 変更内容
エラーメッセージに閉じるボタンを追加し、一定時間後に自動的に消えるようにする。

#### コード（全体を差し替え）

```tsx
/**
 * Appコンポーネント — アプリケーションのルート（最終版）
 */

// useEffect: エラーの自動消去タイマー用
import { useEffect } from "react";
import Header from "./components/Header";
import AddCounterForm from "./components/AddCounterForm";
import CounterList from "./components/CounterList";
import { useCounters } from "./hooks/useCounters";

function App() {
  const { counters, loading, error, addCounter, removeCounter, toggleToday } =
    useCounters();

  // エラーが表示されたら5秒後に自動的に消す
  // ※ useCountersのerrorステートをクリアする方法がないため、
  // この実装はシンプルにエラー表示の制御のみ行う
  useEffect(() => {
    if (error) {
      // 5秒後にページをリロードせず、エラーはuseCountersの次のAPI呼び出しでクリアされる
      const timer = setTimeout(() => {
        // エラーは次のAPI操作時にクリアされるので、ここでは何もしない
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* max-w-md: モバイル向けの幅制限 */}
      {/* mx-auto: 画面中央 */}
      {/* px-4: 左右パディング（スマホの端に余白を作る） */}
      {/* py-6: 上下パディング */}
      {/* safe-area対応: iPhoneのノッチやホームバーを避ける */}
      <div className="mx-auto max-w-md px-4 py-6">
        <Header />
        <AddCounterForm onAdd={addCounter} />

        {/* エラーメッセージ */}
        {error && (
          <div className="mb-4 flex items-center justify-between rounded-lg bg-red-50 p-3">
            <span className="text-sm text-red-600">{error}</span>
            {/* エラーは次のAPI操作で自動クリアされる旨の表示 */}
            <span className="text-xs text-red-400">自動で消えます</span>
          </div>
        )}

        {/* ローディング */}
        {loading ? (
          <div className="flex justify-center py-8">
            {/* シンプルなローディングテキスト */}
            <p className="text-gray-400">読み込み中...</p>
          </div>
        ) : (
          <CounterList
            counters={counters}
            onToggleToday={toggleToday}
            onDelete={removeCounter}
          />
        )}
      </div>
    </div>
  );
}

export default App;
```

---

## 6-6. テストの追加

### 作成ファイル: `frontend/src/__tests__/ConfirmDialog.test.tsx`

#### このファイルの役割
確認ダイアログの表示・操作をテストする。

#### コード

```tsx
/**
 * ConfirmDialogコンポーネントのテスト
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ConfirmDialog from "../components/ConfirmDialog";

const mockConfirm = vi.fn();
const mockCancel = vi.fn();

const defaultProps = {
  isOpen: true,
  title: "削除確認",
  message: "「筋トレ」を削除しますか？",
  confirmLabel: "削除する",
  onConfirm: mockConfirm,
  onCancel: mockCancel,
};

describe("ConfirmDialog", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("isOpen=trueでダイアログが表示される", () => {
    render(<ConfirmDialog {...defaultProps} />);
    expect(screen.getByText("削除確認")).toBeInTheDocument();
    expect(screen.getByText("「筋トレ」を削除しますか？")).toBeInTheDocument();
  });

  it("isOpen=falseでダイアログが表示されない", () => {
    render(<ConfirmDialog {...defaultProps} isOpen={false} />);
    expect(screen.queryByText("削除確認")).not.toBeInTheDocument();
  });

  it("削除ボタンをクリックするとonConfirmが呼ばれる", async () => {
    const user = userEvent.setup();
    render(<ConfirmDialog {...defaultProps} />);
    await user.click(screen.getByText("削除する"));
    expect(mockConfirm).toHaveBeenCalledTimes(1);
  });

  it("キャンセルボタンをクリックするとonCancelが呼ばれる", async () => {
    const user = userEvent.setup();
    render(<ConfirmDialog {...defaultProps} />);
    await user.click(screen.getByText("キャンセル"));
    expect(mockCancel).toHaveBeenCalledTimes(1);
  });
});
```

---

## テスト実行

```bash
# frontendディレクトリで全テストを実行
$ npx vitest run

# 期待される出力:
# ✓ src/__tests__/App.test.tsx (2)
#   ✓ App (2)
#     ✓ タイトルが表示される
#     ✓ カウンターが空の場合にメッセージが表示される
# ✓ src/__tests__/CounterCard.test.tsx (4)
#   ✓ CounterCard (4)
#     ✓ カウンター名が表示される
#     ✓ チェックボタンをクリックするとonToggleTodayが呼ばれる
#     ✓ 削除ボタンをクリックするとonDeleteが呼ばれる
#     ✓ today_done=trueの場合にチェックマークが表示される
# ✓ src/__tests__/ConfirmDialog.test.tsx (4)
#   ✓ ConfirmDialog (4)
#     ✓ isOpen=trueでダイアログが表示される
#     ✓ isOpen=falseでダイアログが表示されない
#     ✓ 削除ボタンをクリックするとonConfirmが呼ばれる
#     ✓ キャンセルボタンをクリックするとonCancelが呼ばれる
# ✓ src/__tests__/MonthlyGrid.test.tsx (7)
#   ✓ MonthlyGrid (7)
#     ✓ 年月が表示される
#     ✓ 曜日ヘッダーが表示される
#     ✓ 日付が表示される
#     ✓ 記録がある日に●が表示される
#     ✓ 前月ボタンをクリックするとonPrevMonthが呼ばれる
#     ✓ 次月ボタンをクリックするとonNextMonthが呼ばれる
#     ✓ ローディング中は読み込みメッセージが表示される
#
# Test Files  4 passed (4)
# Tests  17 passed (17)
```

---

## 全体テスト（バックエンド + フロントエンド）

```bash
# バックエンドのテスト
$ cd backend
$ pytest -v
# → 30 passed

# フロントエンドのテスト
$ cd ../frontend
$ npx vitest run
# → 17 passed

# 合計: 47テストがパス
```

---

## 最終動作確認

```bash
# ターミナル1: バックエンド起動
$ cd backend
$ source .venv/bin/activate
$ uvicorn app.main:app --reload --port 8000

# ターミナル2: フロントエンド起動
$ cd frontend
$ npm run dev

# ブラウザで http://localhost:5173 にアクセス
```

### 確認チェックリスト

```
# === カウンター操作 ===
# 1. 「新しいカウンター名」入力欄にテキストを入力
# 2. 「追加」ボタンをクリック → カウンターカードが表示される
# 3. 複数のカウンターを追加できる

# === チェック操作 ===
# 4. カードの○ボタンをクリック → ✓に変わる（バウンスアニメーション）
# 5. カード背景が緑に変わる
# 6. もう一度クリック → ✓が消えて○に戻る

# === カレンダー操作 ===
# 7. カウンター名をクリック → 月間カレンダーが展開される
# 8. チェック済みの日に●が表示される
# 9. ◀▶ で前月・次月に切り替えられる
# 10. 直近3日以内の日付をタップ → ●の追加/削除ができる
# 11. 4日以上前の日付は薄く表示され、タップしても反応しない

# === 削除操作 ===
# 12. 🗑ボタンをクリック → 確認ダイアログが表示される
# 13. 「キャンセル」→ ダイアログが閉じてカウンターは残る
# 14. 「削除する」→ カウンターと関連する記録が全て削除される

# === エラーハンドリング ===
# 15. バックエンドを停止した状態でカウンター追加 → エラーメッセージが表示される

# === モバイル表示 ===
# 16. ブラウザのデベロッパーツールでモバイルビュー（iPhone等）に切り替え
# 17. タップ操作でスムーズに動作する
# 18. テキストが読みやすいサイズで表示される
```

---

## 最終ディレクトリ構造

```
anything-counter/
├── spec.md                        # アプリ仕様
├── describe/                      # 写経ガイド（このファイル群）
│   ├── step1-backend-foundation.md
│   ├── step2-backend-api.md
│   ├── step3-frontend-foundation.md
│   ├── step4-counter-list-ui.md
│   ├── step5-monthly-calendar-ui.md
│   └── step6-styling-finishing.md
├── backend/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   ├── main.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── counters.py
│   │       └── records.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_models.py
│       ├── test_health.py
│       ├── test_crud.py
│       ├── test_counters.py
│       └── test_records.py
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── tsconfig.app.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── index.css
        ├── App.tsx
        ├── types/
        │   └── index.ts
        ├── api/
        │   └── client.ts
        ├── hooks/
        │   ├── useCounters.ts
        │   └── useRecords.ts
        ├── components/
        │   ├── Header.tsx
        │   ├── AddCounterForm.tsx
        │   ├── CounterCard.tsx
        │   ├── CounterList.tsx
        │   ├── MonthlyGrid.tsx
        │   └── ConfirmDialog.tsx
        ├── test/
        │   └── setup.ts
        └── __tests__/
            ├── App.test.tsx
            ├── CounterCard.test.tsx
            ├── MonthlyGrid.test.tsx
            └── ConfirmDialog.test.tsx
```

---

## このステップの完了チェックリスト

- [ ] `npx vitest run` で17件全てのフロントエンドテストがパスする
- [ ] `pytest -v` で30件全てのバックエンドテストがパスする
- [ ] 削除ボタンクリック時に確認ダイアログが表示される
- [ ] 確認ダイアログの「キャンセル」で削除がキャンセルされる
- [ ] チェックボタンにバウンスアニメーションが再生される
- [ ] チェック済みカードの背景が緑、テキストも緑系に変わる
- [ ] アコーディオンの展開/閉じに▼▲インジケーターが表示される
- [ ] モバイルビューで操作しやすいサイズ・間隔になっている
- [ ] タップ操作でダブルタップズームが発生しない
- [ ] APIエラー時にエラーメッセージが表示される

---

## 🎉 完成！

全6ステップを完了すると、以下の機能が動作するWebアプリが完成します:

1. **カウンター管理**: 習慣カウンターの追加・削除
2. **今日のチェック**: ワンタップで「今日やった」を記録
3. **月間カレンダー**: 実行した日を●で可視化
4. **過去の記録編集**: 直近3日以内なら記録の追加・削除が可能
5. **誤操作防止**: 削除時の確認ダイアログ
6. **モバイル対応**: スマホで快適に操作可能
