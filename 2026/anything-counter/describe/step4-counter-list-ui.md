# Step 4: カウンター一覧UI（Header + AddCounterForm + CounterList + CounterCard）

## このステップで作るもの

- Header コンポーネント（アプリタイトル）
- AddCounterForm コンポーネント（カウンター追加フォーム）
- useCounters カスタムフック（カウンターのデータ取得・操作）
- CounterCard コンポーネント（個別カウンターの表示・チェック・削除）
- CounterList コンポーネント（カウンター一覧の表示）
- App.tsx の更新（全コンポーネントの統合）

**完了後の状態**: カウンターの一覧表示・新規追加・今日のチェック切り替え・削除ができる。バックエンドAPIと連携して動作する。

## 前提条件

- Step 3 が完了していること（フロントエンド基盤が動作する状態）
- `frontend/` ディレクトリにいること
- バックエンドサーバーが起動していること（`uvicorn app.main:app --reload --port 8000`）

---

## 4-1. Header コンポーネント

### 作成ファイル: `frontend/src/components/Header.tsx`

#### このファイルの役割
アプリケーションのヘッダー部分。タイトルを表示する。

#### コード

```tsx
/**
 * Headerコンポーネント — アプリケーションのヘッダー
 * タイトルを表示する
 */
function Header() {
  return (
    // mb-6: 下方向のマージン（1.5rem = 24px）
    <header className="mb-6">
      {/* text-2xl: フォントサイズ 1.5rem */}
      {/* font-bold: 太字 */}
      {/* text-gray-800: 濃いグレーのテキスト色 */}
      <h1 className="text-2xl font-bold text-gray-800">
        Anything Counter
      </h1>
    </header>
  );
}

export default Header;
```

---

## 4-2. useCounters カスタムフック

### 作成ファイル: `frontend/src/hooks/useCounters.ts`

#### このファイルの役割
カウンターのデータ取得・作成・削除・今日のチェック切り替えのロジックを集約する。コンポーネントからビジネスロジックを分離して再利用性を高める。

#### コード

```typescript
/**
 * useCounters カスタムフック
 * カウンターのCRUD操作とローディング状態を管理する
 */

// useState: コンポーネントの状態を管理するReactフック
// useEffect: 副作用（API呼び出しなど）を実行するReactフック
// useCallback: 関数をメモ化して不要な再生成を防ぐReactフック
import { useState, useEffect, useCallback } from "react";
// 型定義
import type { Counter } from "../types";
// APIクライアント関数群
import {
  fetchCounters,
  createCounter as apiCreateCounter,
  deleteCounter as apiDeleteCounter,
  createRecord as apiCreateRecord,
  deleteRecord as apiDeleteRecord,
} from "../api/client";

/**
 * useCountersの戻り値の型定義
 */
type UseCountersReturn = {
  /** カウンター一覧 */
  counters: Counter[];
  /** データ読み込み中かどうか */
  loading: boolean;
  /** エラーメッセージ（エラーがなければnull） */
  error: string | null;
  /** カウンターを新規作成する関数 */
  addCounter: (name: string) => Promise<void>;
  /** カウンターを削除する関数 */
  removeCounter: (id: number) => Promise<void>;
  /** 今日のチェックを切り替える関数（done→削除、undone→作成） */
  toggleToday: (counter: Counter) => Promise<void>;
};

/**
 * カウンターのCRUD操作を提供するカスタムフック
 *
 * 使い方:
 *   const { counters, loading, addCounter, removeCounter, toggleToday } = useCounters();
 */
export function useCounters(): UseCountersReturn {
  // カウンター一覧の状態
  const [counters, setCounters] = useState<Counter[]>([]);
  // ローディング状態
  const [loading, setLoading] = useState(true);
  // エラー状態
  const [error, setError] = useState<string | null>(null);

  /**
   * カウンター一覧をAPIから取得する関数
   * useCallbackでメモ化して、依存配列が変わらない限り同じ関数参照を保持する
   */
  const load = useCallback(async () => {
    try {
      setError(null);
      // APIからカウンター一覧を取得
      const data = await fetchCounters();
      // 状態を更新（再レンダリングが発生する）
      setCounters(data);
    } catch (e) {
      // エラーメッセージを設定
      setError(e instanceof Error ? e.message : "データの取得に失敗しました");
    } finally {
      // ローディング状態を解除（成功でも失敗でも）
      setLoading(false);
    }
  }, []);

  // コンポーネントのマウント時にカウンター一覧を取得
  // 第2引数の[load]が変わらない限り、再実行されない
  useEffect(() => {
    load();
  }, [load]);

  /**
   * カウンターを新規作成する
   * @param name - カウンター名
   */
  const addCounter = useCallback(
    async (name: string) => {
      try {
        setError(null);
        // APIにPOSTリクエスト
        await apiCreateCounter(name);
        // 一覧を再取得して最新状態を反映
        await load();
      } catch (e) {
        setError(e instanceof Error ? e.message : "カウンターの作成に失敗しました");
      }
    },
    [load],
  );

  /**
   * カウンターを削除する
   * @param id - 削除するカウンターのID
   */
  const removeCounter = useCallback(
    async (id: number) => {
      try {
        setError(null);
        // APIにDELETEリクエスト
        await apiDeleteCounter(id);
        // 一覧を再取得
        await load();
      } catch (e) {
        setError(e instanceof Error ? e.message : "カウンターの削除に失敗しました");
      }
    },
    [load],
  );

  /**
   * 今日のチェックを切り替える（トグル）
   * - today_done === true → 今日の記録を削除
   * - today_done === false → 今日の記録を作成
   * @param counter - 対象のカウンター
   */
  const toggleToday = useCallback(
    async (counter: Counter) => {
      try {
        setError(null);
        // 今日の日付を "YYYY-MM-DD" 形式で取得
        const today = new Date().toISOString().split("T")[0];
        if (counter.today_done) {
          // チェック済み → 記録を削除
          await apiDeleteRecord(counter.id, today);
        } else {
          // 未チェック → 記録を作成
          await apiCreateRecord(counter.id, today);
        }
        // 一覧を再取得してtoday_doneの状態を更新
        await load();
      } catch (e) {
        setError(e instanceof Error ? e.message : "記録の更新に失敗しました");
      }
    },
    [load],
  );

  // フックの戻り値（コンポーネントがこれらを使う）
  return { counters, loading, error, addCounter, removeCounter, toggleToday };
}
```

---

## 4-3. CounterCard コンポーネント

### 作成ファイル: `frontend/src/components/CounterCard.tsx`

#### このファイルの役割
個別のカウンターを表示するカード。チェック状態の切り替え、カウンター名の表示、削除ボタンを持つ。

#### コード

```tsx
/**
 * CounterCardコンポーネント — 個別カウンターの表示カード
 *
 * 機能:
 * - タップでtoday_doneを切り替え
 * - チェック済みカードの背景色変更
 * - 削除ボタン
 */

// Counter型のインポート
import type { Counter } from "../types";

/**
 * CounterCardのprops（親コンポーネントから受け取るデータ）
 */
type Props = {
  /** 表示するカウンターデータ */
  counter: Counter;
  /** 今日のチェックを切り替える関数（親から渡される） */
  onToggleToday: (counter: Counter) => void;
  /** 削除関数（親から渡される） */
  onDelete: (id: number) => void;
  /** カードクリック時の関数（アコーディオン展開用、Step 5で使用） */
  onSelect: (id: number) => void;
  /** このカードが選択（展開）中かどうか */
  isSelected: boolean;
};

function CounterCard({ counter, onToggleToday, onDelete, onSelect, isSelected }: Props) {
  return (
    // カード全体のコンテナ
    // rounded-lg: 角丸（0.5rem）
    // shadow-sm: 薄い影
    // transition-colors: 背景色変更時のアニメーション
    // duration-200: アニメーション時間200ms
    // today_doneによって背景色を変える
    <div
      className={`rounded-lg border p-4 shadow-sm transition-colors duration-200 ${
        counter.today_done
          ? "border-green-300 bg-green-50"  // チェック済み: 緑系
          : "border-gray-200 bg-white"       // 未チェック: 白
      }`}
    >
      {/* カードの上段: チェックボタン + カウンター名 + 削除ボタン */}
      <div className="flex items-center gap-3">
        {/* チェックボタン */}
        {/* flex-shrink-0: フレックスアイテムが縮小しないようにする */}
        <button
          onClick={(e) => {
            // イベントの伝播を止める（カードのonClick発火を防ぐ）
            e.stopPropagation();
            onToggleToday(counter);
          }}
          className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full border-2 transition-colors"
          // aria-label: スクリーンリーダー用のラベル
          aria-label={counter.today_done ? "チェックを外す" : "チェックする"}
        >
          {/* チェック済みなら ✓ マークを表示 */}
          {counter.today_done && (
            <span className="text-green-600 text-lg">✓</span>
          )}
        </button>

        {/* カウンター名（クリックでアコーディオン展開） */}
        {/* flex-1: 残りのスペースを全て使う */}
        {/* cursor-pointer: マウスカーソルをポインターにする */}
        {/* truncate: テキストが長い場合に省略記号（...）で切り詰める */}
        <span
          className="flex-1 cursor-pointer truncate text-gray-800"
          onClick={() => onSelect(counter.id)}
        >
          {counter.name}
        </span>

        {/* 削除ボタン */}
        {/* text-gray-400 hover:text-red-500: ホバーで赤色に変化 */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(counter.id);
          }}
          className="flex-shrink-0 text-gray-400 transition-colors hover:text-red-500"
          aria-label="削除"
        >
          {/* ゴミ箱アイコン（テキスト表現） */}
          🗑
        </button>
      </div>

      {/* アコーディオン展開部分（Step 5で MonthlyGrid を追加する） */}
      {isSelected && (
        <div className="mt-4 border-t pt-4">
          {/* Step 5でMonthlyGridコンポーネントをここに配置 */}
          <p className="text-sm text-gray-400">カレンダーはStep 5で実装します</p>
        </div>
      )}
    </div>
  );
}

export default CounterCard;
```

---

## 4-4. CounterList コンポーネント

### 作成ファイル: `frontend/src/components/CounterList.tsx`

#### このファイルの役割
カウンター一覧を表示するコンテナコンポーネント。CounterCardを繰り返しレンダリングする。

#### コード

```tsx
/**
 * CounterListコンポーネント — カウンター一覧の表示
 * CounterCardを繰り返しレンダリングし、選択状態を管理する
 */

// useState: アコーディオンの選択状態を管理するために使用
import { useState } from "react";
// 型定義
import type { Counter } from "../types";
// 個別カウンターカードコンポーネント
import CounterCard from "./CounterCard";

/**
 * CounterListのprops
 */
type Props = {
  /** カウンター一覧データ */
  counters: Counter[];
  /** 今日のチェックを切り替える関数 */
  onToggleToday: (counter: Counter) => void;
  /** カウンターを削除する関数 */
  onDelete: (id: number) => void;
};

function CounterList({ counters, onToggleToday, onDelete }: Props) {
  // 現在選択（アコーディオン展開）中のカウンターID
  // null = どれも展開していない
  const [selectedId, setSelectedId] = useState<number | null>(null);

  /**
   * カードの選択をトグルする
   * 同じカードを再クリックしたら閉じる、別のカードなら切り替える
   */
  const handleSelect = (id: number) => {
    setSelectedId((prev) => (prev === id ? null : id));
  };

  // カウンターが0件の場合のメッセージ
  if (counters.length === 0) {
    return (
      <p className="text-center text-gray-400">
        カウンターがありません。上のフォームから追加してください。
      </p>
    );
  }

  return (
    // space-y-3: 子要素間の縦方向の間隔（0.75rem = 12px）
    <div className="space-y-3">
      {/* カウンター一覧をmap()で繰り返しレンダリング */}
      {/* key={counter.id}: Reactが各要素を一意に識別するために必要 */}
      {counters.map((counter) => (
        <CounterCard
          key={counter.id}
          counter={counter}
          onToggleToday={onToggleToday}
          onDelete={onDelete}
          onSelect={handleSelect}
          isSelected={selectedId === counter.id}
        />
      ))}
    </div>
  );
}

export default CounterList;
```

---

## 4-5. AddCounterForm コンポーネント

### 作成ファイル: `frontend/src/components/AddCounterForm.tsx`

#### このファイルの役割
カウンター追加用の入力フォーム。テキスト入力と送信ボタンを持つ。

#### コード

```tsx
/**
 * AddCounterFormコンポーネント — カウンター追加フォーム
 * テキスト入力と送信ボタンで新しいカウンターを追加する
 */

// useState: 入力値の状態管理
// FormEvent: フォーム送信イベントの型
import { useState, type FormEvent } from "react";

/**
 * AddCounterFormのprops
 */
type Props = {
  /** カウンター追加関数（親から渡される） */
  onAdd: (name: string) => Promise<void>;
};

function AddCounterForm({ onAdd }: Props) {
  // 入力フィールドの値を管理する状態
  const [name, setName] = useState("");
  // 送信中かどうか（ボタン連打防止用）
  const [submitting, setSubmitting] = useState(false);

  /**
   * フォーム送信ハンドラ
   * @param e - フォーム送信イベント
   */
  const handleSubmit = async (e: FormEvent) => {
    // デフォルトのフォーム送信（ページリロード）を防止
    e.preventDefault();
    // 空白のみの入力を防止（trimで前後の空白を除去）
    const trimmed = name.trim();
    if (!trimmed) return;

    setSubmitting(true);
    try {
      // 親コンポーネントに追加を依頼
      await onAdd(trimmed);
      // 成功したら入力フィールドをクリア
      setName("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    // mb-6: 下方向のマージン
    // flex: フレックスボックスで横並び
    // gap-2: 子要素間の間隔
    <form onSubmit={handleSubmit} className="mb-6 flex gap-2">
      {/* テキスト入力フィールド */}
      {/* flex-1: 残りスペースを全て使う */}
      {/* rounded-lg: 角丸 */}
      {/* border: 枠線 */}
      {/* px-3 py-2: 内側の余白（水平12px、垂直8px） */}
      {/* focus:outline-none focus:ring-2: フォーカス時に枠線を強調 */}
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="新しいカウンター名"
        className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
        // 送信中は入力を無効化
        disabled={submitting}
      />
      {/* 追加ボタン */}
      {/* bg-blue-500: 青い背景 */}
      {/* text-white: 白いテキスト */}
      {/* disabled:opacity-50: 無効時に半透明 */}
      <button
        type="submit"
        disabled={submitting || !name.trim()}
        className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
      >
        追加
      </button>
    </form>
  );
}

export default AddCounterForm;
```

---

## 4-6. App.tsx の更新

### 更新ファイル: `frontend/src/App.tsx`

#### 変更内容
全コンポーネントを統合して、カウンター管理画面を完成させる。

#### コード（全体を差し替え）

```tsx
/**
 * Appコンポーネント — アプリケーションのルート
 * Header + AddCounterForm + CounterList を統合する
 */

// 各コンポーネントをインポート
import Header from "./components/Header";
import AddCounterForm from "./components/AddCounterForm";
import CounterList from "./components/CounterList";
// カウンター操作のカスタムフック
import { useCounters } from "./hooks/useCounters";

function App() {
  // カスタムフックからデータと操作関数を取得
  const { counters, loading, error, addCounter, removeCounter, toggleToday } =
    useCounters();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-md p-4">
        {/* ヘッダー */}
        <Header />

        {/* カウンター追加フォーム */}
        <AddCounterForm onAdd={addCounter} />

        {/* エラーメッセージ表示 */}
        {error && (
          // bg-red-50: 薄い赤の背景
          // text-red-600: 赤いテキスト
          // rounded-lg: 角丸
          // p-3: 内側の余白
          // mb-4: 下マージン
          <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
            {error}
          </div>
        )}

        {/* ローディング表示 */}
        {loading ? (
          <p className="text-center text-gray-400">読み込み中...</p>
        ) : (
          /* カウンター一覧 */
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

## 4-7. テストの作成

### 作成ファイル: `frontend/src/__tests__/CounterCard.test.tsx`

#### このファイルの役割
CounterCardコンポーネントの表示と操作をテストする。

#### コード

```tsx
/**
 * CounterCardコンポーネントのテスト
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import CounterCard from "../components/CounterCard";
import type { Counter } from "../types";

// テスト用のモックカウンターデータ
const mockCounter: Counter = {
  id: 1,
  name: "筋トレ",
  created_at: "2026-01-01T00:00:00",
  sort_order: 0,
  today_done: false,
};

// モック関数（呼び出されたかどうかを検証できる）
const mockToggle = vi.fn();
const mockDelete = vi.fn();
const mockSelect = vi.fn();

describe("CounterCard", () => {
  // 各テストの前にモック関数をリセット
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("カウンター名が表示される", () => {
    render(
      <CounterCard
        counter={mockCounter}
        onToggleToday={mockToggle}
        onDelete={mockDelete}
        onSelect={mockSelect}
        isSelected={false}
      />,
    );
    // "筋トレ" というテキストが画面に存在することを確認
    expect(screen.getByText("筋トレ")).toBeInTheDocument();
  });

  it("チェックボタンをクリックするとonToggleTodayが呼ばれる", async () => {
    // userEventのセットアップ（非同期操作のシミュレーション）
    const user = userEvent.setup();
    render(
      <CounterCard
        counter={mockCounter}
        onToggleToday={mockToggle}
        onDelete={mockDelete}
        onSelect={mockSelect}
        isSelected={false}
      />,
    );
    // "チェックする" ラベルのボタンをクリック
    await user.click(screen.getByLabelText("チェックする"));
    // mockToggleがmockCounterを引数に呼ばれたことを確認
    expect(mockToggle).toHaveBeenCalledWith(mockCounter);
  });

  it("削除ボタンをクリックするとonDeleteが呼ばれる", async () => {
    const user = userEvent.setup();
    render(
      <CounterCard
        counter={mockCounter}
        onToggleToday={mockToggle}
        onDelete={mockDelete}
        onSelect={mockSelect}
        isSelected={false}
      />,
    );
    await user.click(screen.getByLabelText("削除"));
    // mockDeleteがカウンターIDを引数に呼ばれたことを確認
    expect(mockDelete).toHaveBeenCalledWith(1);
  });

  it("today_done=trueの場合にチェックマークが表示される", () => {
    const doneCounter = { ...mockCounter, today_done: true };
    render(
      <CounterCard
        counter={doneCounter}
        onToggleToday={mockToggle}
        onDelete={mockDelete}
        onSelect={mockSelect}
        isSelected={false}
      />,
    );
    // ✓ マークが表示されることを確認
    expect(screen.getByText("✓")).toBeInTheDocument();
  });
});
```

### 更新ファイル: `frontend/src/__tests__/App.test.tsx`

#### 変更内容
App全体のテストを更新する。APIをモックして動作を確認する。

#### コード（全体を差し替え）

```tsx
/**
 * Appコンポーネントのテスト
 * APIクライアントをモックしてコンポーネントの表示を検証する
 */
import { render, screen, waitFor } from "@testing-library/react";
import App from "../App";

// APIクライアントモジュール全体をモック化
// vi.mock: 指定モジュールのエクスポートをすべてモック関数に置き換える
vi.mock("../api/client", () => ({
  fetchCounters: vi.fn().mockResolvedValue([]),
  createCounter: vi.fn(),
  deleteCounter: vi.fn(),
  createRecord: vi.fn(),
  deleteRecord: vi.fn(),
}));

describe("App", () => {
  it("タイトルが表示される", async () => {
    render(<App />);
    // waitFor: 非同期操作（API呼び出し）の完了を待つ
    await waitFor(() => {
      expect(screen.getByText("Anything Counter")).toBeInTheDocument();
    });
  });

  it("カウンターが空の場合にメッセージが表示される", async () => {
    render(<App />);
    await waitFor(() => {
      expect(
        screen.getByText("カウンターがありません。上のフォームから追加してください。"),
      ).toBeInTheDocument();
    });
  });
});
```

---

## テスト実行

```bash
# frontendディレクトリで実行
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
#
# Test Files  2 passed (2)
# Tests  6 passed (6)
```

---

## 手動での動作確認

```bash
# バックエンドを起動（別ターミナル）
$ cd backend
$ uvicorn app.main:app --reload --port 8000

# フロントエンドを起動
$ cd frontend
$ npm run dev

# ブラウザで http://localhost:5173 にアクセス
#
# 確認項目:
# 1. "Anything Counter" タイトルが表示される
# 2. 入力フォームと「追加」ボタンが表示される
# 3. カウンター名を入力して「追加」をクリック → カウンターカードが追加される
# 4. カードの○ボタンをクリック → ✓に変わり、カード背景が緑になる
# 5. カードの🗑ボタンをクリック → カウンターが削除される
# 6. カード名をクリック → アコーディオンが展開される（プレースホルダーテキスト）
```

---

## このステップのディレクトリ構造

```
frontend/src/
├── main.tsx
├── index.css
├── App.tsx                    # ← 更新（コンポーネント統合）
├── vite-env.d.ts
├── types/
│   └── index.ts
├── api/
│   └── client.ts
├── hooks/
│   └── useCounters.ts        # ← 新規
├── components/
│   ├── Header.tsx             # ← 新規
│   ├── AddCounterForm.tsx     # ← 新規
│   ├── CounterCard.tsx        # ← 新規
│   └── CounterList.tsx        # ← 新規
├── test/
│   └── setup.ts
└── __tests__/
    ├── App.test.tsx           # ← 更新
    └── CounterCard.test.tsx   # ← 新規
```

---

## このステップの完了チェックリスト

- [ ] `npx vitest run` で6件全てのテストがパスする
- [ ] カウンターを追加できる（フォームから名前入力 → 追加ボタン）
- [ ] カウンター一覧が表示される
- [ ] 今日のチェックを切り替えられる（○ ↔ ✓）
- [ ] チェック済みカードの背景が緑に変わる
- [ ] カウンターを削除できる
- [ ] カードをクリックするとアコーディオンが展開/閉じる
- [ ] 空の状態で「カウンターがありません」メッセージが表示される
