# Step 3: フロントエンド基盤（React + TypeScript + Vite + Tailwind CSS）

## このステップで作るもの

- Vite + React + TypeScript プロジェクトの作成
- Tailwind CSS の導入
- TypeScript 型定義（Counter, Record）
- API クライアント（fetch ラッパー）
- Vitest + React Testing Library のセットアップ
- Vite の API プロキシ設定

**完了後の状態**: フロントエンドの開発基盤が整い、`npm run dev` でViteの開発サーバーが起動する。APIクライアントからバックエンドへリクエストが送れる状態になる。

## 前提条件

- Step 2 が完了していること（バックエンドが動作する状態）
- Node.js 18 以上がインストールされていること
- npm が使えること
- `anything-counter/` ディレクトリにいること

---

## 3-1. Vite プロジェクトの作成

### 実行コマンド

```bash
# anything-counter/ ディレクトリで実行
# npm create vite@latest でプロジェクトを作成
# -- --template react-ts: React + TypeScriptテンプレートを使用
$ npm create vite@latest frontend -- --template react-ts

# 期待される出力:
# Scaffolding project in /path/to/anything-counter/frontend...
# Done. Now run:
#   cd frontend
#   npm install
#   npm run dev

# フロントエンドディレクトリに移動してパッケージをインストール
$ cd frontend
$ npm install
```

---

## 3-2. 不要ファイルの削除

Vite テンプレートにはデモ用ファイルが含まれるので、不要なものを削除する。

```bash
# Viteのデモ用CSS・アセットを削除
$ rm src/App.css
$ rm src/assets/react.svg
$ rm public/vite.svg
```

---

## 3-3. Tailwind CSS の導入

### 実行コマンド

```bash
# Tailwind CSS と Viteプラグインをインストール
$ npm install -D tailwindcss @tailwindcss/vite
```

### 更新ファイル: `frontend/vite.config.ts`

#### このファイルの役割
Viteのビルド設定。Tailwind CSSプラグインとAPIプロキシを設定する。

#### コード

```typescript
// defineConfig: Viteの設定オブジェクトを型安全に定義するヘルパー関数
import { defineConfig } from "vite";
// react: Viteでreactを使うためのプラグイン（JSX変換、Fast Refreshなど）
import react from "@vitejs/plugin-react";
// tailwindcss: TailwindCSSをViteに統合するプラグイン
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  // プラグインの登録
  plugins: [
    // React用プラグイン（JSXのトランスパイル、HMR対応）
    react(),
    // Tailwind CSS用プラグイン（PostCSS不要でTailwindが使える）
    tailwindcss(),
  ],
  // 開発サーバーの設定
  server: {
    // APIプロキシ設定: /api へのリクエストをバックエンド（FastAPI）に転送
    // フロントエンド（:5173）とバックエンド（:8000）が別ポートで動くため、
    // プロキシを使ってCORSの問題を回避する
    proxy: {
      "/api": {
        // 転送先のURL（FastAPIサーバー）
        target: "http://localhost:8000",
        // オリジンヘッダーをターゲットに合わせて書き換える
        changeOrigin: true,
      },
    },
  },
});
```

### 更新ファイル: `frontend/src/index.css`

#### このファイルの役割
Tailwind CSS を読み込むためのエントリポイント。`@import "tailwindcss"` でTailwindの全ユーティリティクラスが使えるようになる。

#### コード

```css
/* Tailwind CSS のインポート */
/* これ1行でTailwindの全ユーティリティクラス（flex, p-4, text-lgなど）が使えるようになる */
@import "tailwindcss";
```

### 実行・確認

```bash
# Tailwindが正しく動作するか確認（開発サーバーを起動）
$ npm run dev

# ブラウザで http://localhost:5173 にアクセス
# エラーなく表示されればOK（内容はまだデフォルト）
```

---

## 3-4. TypeScript 型定義

### 作成ファイル: `frontend/src/types/index.ts`

#### このファイルの役割
バックエンドAPIのレスポンス型をTypeScriptで定義する。フロントエンド全体でこの型を使い回す。

#### コード

```typescript
/**
 * カウンターの型定義
 * バックエンドの GET /api/counters レスポンスに対応
 */
export type Counter = {
  /** データベースの自動採番ID */
  id: number;
  /** カウンター名（例: "筋トレ", "読書"） */
  name: string;
  /** 作成日時（ISO8601形式の文字列） */
  created_at: string;
  /** 表示順序（将来のドラッグ&ドロップ用） */
  sort_order: number;
  /** 今日の実行記録が存在するかどうか（APIが算出する仮想フィールド） */
  today_done: boolean;
};

/**
 * 実行記録の型定義
 * バックエンドの GET /api/counters/{id}/records レスポンスに対応
 */
export type Record = {
  /** データベースの自動採番ID */
  id: number;
  /** 紐づくカウンターのID */
  counter_id: number;
  /** 実行日（"YYYY-MM-DD"形式） */
  date: string;
  /** 作成日時 */
  created_at: string;
};
```

### 実行・確認

```bash
# ディレクトリを作成
$ mkdir -p src/types

# TypeScriptの型チェックが通ることを確認
$ npx tsc --noEmit
```

---

## 3-5. API クライアント

### 作成ファイル: `frontend/src/api/client.ts`

#### このファイルの役割
バックエンドAPIへのHTTPリクエストを行う関数群。fetch APIのラッパーとして、共通のエラーハンドリングとベースURL設定を提供する。

#### コード

```typescript
/**
 * APIクライアント — バックエンドへのHTTPリクエストを行うfetchラッパー
 *
 * Viteのプロキシ設定により、/api へのリクエストは自動的に
 * http://localhost:8000 に転送される
 */

// APIのベースURL（Viteプロキシ経由なので相対パスでOK）
const BASE_URL = "/api";

/**
 * APIエラー時にthrowするカスタムエラークラス
 * HTTPステータスコードとエラーメッセージを保持する
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    // Errorクラスのコンストラクタを呼び出し
    super(message);
    // instanceofが正しく動作するようにプロトタイプを設定
    this.name = "ApiError";
  }
}

/**
 * 共通のfetchラッパー関数
 * 全てのAPIリクエストはこの関数を経由する
 *
 * @param path - APIパス（例: "/counters"）。BASE_URLが自動付与される
 * @param options - fetchのオプション（method, body, headersなど）
 * @returns レスポンスのJSONデータ、または204の場合はnull
 * @throws ApiError - HTTPエラー時
 */
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  // fetchでHTTPリクエストを送信
  const response = await fetch(`${BASE_URL}${path}`, {
    // Content-Typeヘッダーをデフォルトで設定（JSONを送受信するため）
    headers: {
      "Content-Type": "application/json",
    },
    // 呼び出し側のオプションで上書き可能
    ...options,
  });

  // HTTPエラーの場合（4xx, 5xx）
  if (!response.ok) {
    // レスポンスボディからエラーメッセージを取得
    const error = await response.json().catch(() => ({ detail: "エラーが発生しました" }));
    throw new ApiError(response.status, error.detail || "エラーが発生しました");
  }

  // 204 No Content の場合はボディがないのでnullを返す
  if (response.status === 204) {
    return null as T;
  }

  // 正常時はJSONをパースして返す
  return response.json();
}

// ============================
// カウンター API
// ============================

/** カウンター型（ここではインポートせず、呼び出し側で型を指定する） */
import type { Counter, Record } from "../types";

/**
 * カウンター一覧を取得する
 * GET /api/counters
 */
export async function fetchCounters(): Promise<Counter[]> {
  return request<Counter[]>("/counters");
}

/**
 * 新しいカウンターを作成する
 * POST /api/counters
 */
export async function createCounter(name: string): Promise<Counter> {
  return request<Counter>("/counters", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

/**
 * カウンターを削除する
 * DELETE /api/counters/{id}
 */
export async function deleteCounter(id: number): Promise<void> {
  return request<void>(`/counters/${id}`, {
    method: "DELETE",
  });
}

// ============================
// 記録 API
// ============================

/**
 * 指定カウンターの月別記録を取得する
 * GET /api/counters/{id}/records?year=YYYY&month=M
 */
export async function fetchRecords(
  counterId: number,
  year: number,
  month: number,
): Promise<Record[]> {
  return request<Record[]>(
    `/counters/${counterId}/records?year=${year}&month=${month}`,
  );
}

/**
 * 実行記録を作成する
 * POST /api/counters/{id}/records
 */
export async function createRecord(
  counterId: number,
  date: string,
): Promise<Record> {
  return request<Record>(`/counters/${counterId}/records`, {
    method: "POST",
    body: JSON.stringify({ date }),
  });
}

/**
 * 実行記録を削除する
 * DELETE /api/counters/{id}/records/{date}
 */
export async function deleteRecord(
  counterId: number,
  date: string,
): Promise<void> {
  return request<void>(`/counters/${counterId}/records/${date}`, {
    method: "DELETE",
  });
}
```

### 実行・確認

```bash
# ディレクトリを作成
$ mkdir -p src/api

# TypeScriptの型チェック
$ npx tsc --noEmit
```

---

## 3-6. Vitest + React Testing Library のセットアップ

### 実行コマンド

```bash
# テスト関連パッケージをインストール
# vitest: Viteベースのテストランナー（Jestの代替、Viteと同じ設定を共有）
# @testing-library/react: Reactコンポーネントのテスト用ユーティリティ
# @testing-library/jest-dom: DOMアサーション拡張（toBeInTheDocumentなど）
# @testing-library/user-event: ユーザー操作シミュレーション（click, typeなど）
# jsdom: ブラウザ環境のシミュレーション（Node.jsでDOMを使うため）
$ npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

### 更新ファイル: `frontend/vite.config.ts`

#### 変更内容
Vitest の設定を追加する（テスト環境の指定）。

#### コード（全体を差し替え）

```typescript
// defineConfig: Viteの設定オブジェクトを型安全に定義するヘルパー関数
import { defineConfig } from "vite";
// react: Viteでreactを使うためのプラグイン
import react from "@vitejs/plugin-react";
// tailwindcss: TailwindCSSをViteに統合するプラグイン
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  // Vitestの設定（vite.config.ts内に記述できる）
  test: {
    // テスト環境: jsdom（ブラウザのDOMをNode.js上でシミュレーション）
    environment: "jsdom",
    // グローバルAPIを有効化（describe, it, expectをimportなしで使える）
    globals: true,
    // テスト実行前に読み込むセットアップファイル
    setupFiles: "./src/test/setup.ts",
  },
});
```

### 作成ファイル: `frontend/src/test/setup.ts`

#### このファイルの役割
全テストの実行前に読み込まれるセットアップファイル。jest-dom のカスタムマッチャーを登録する。

#### コード

```typescript
// @testing-library/jest-dom: DOMに対するカスタムアサーションを追加
// toBeInTheDocument(), toHaveTextContent(), toBeVisible() などが使えるようになる
import "@testing-library/jest-dom";
```

### 更新ファイル: `frontend/tsconfig.app.json`

#### 変更内容
TypeScriptにVitestのグローバル型を認識させる。

`compilerOptions` の中に以下を追加する:

```json
{
  "compilerOptions": {
    "types": ["vitest/globals"]
  }
}
```

> **注意**: 既存の `compilerOptions` に `"types": ["vitest/globals"]` を追加する。他の設定は変更しない。

### 実行・確認

```bash
# ディレクトリを作成
$ mkdir -p src/test

# Vitestが起動できることを確認（テストファイルがまだないので "no test files found" と出るのが正常）
$ npx vitest run
# 期待される出力: "No test files found"
```

---

## 3-7. App.tsx の初期化

### 更新ファイル: `frontend/src/App.tsx`

#### このファイルの役割
アプリケーションのルートコンポーネント。現時点では最小限のプレースホルダーを表示する。

#### コード

```tsx
/**
 * Appコンポーネント — アプリケーションのルート
 * 現時点ではプレースホルダーのみ。Step 4以降で実装を追加する。
 */
function App() {
  return (
    // min-h-screen: 画面の高さいっぱいに表示
    // bg-gray-50: 薄いグレーの背景色
    <div className="min-h-screen bg-gray-50">
      {/* max-w-md: モバイルファーストの幅制限（約28rem = 448px） */}
      {/* mx-auto: 左右中央揃え */}
      {/* p-4: 内側の余白（1rem = 16px） */}
      <div className="mx-auto max-w-md p-4">
        {/* text-2xl: フォントサイズ（1.5rem） */}
        {/* font-bold: 太字 */}
        <h1 className="text-2xl font-bold text-gray-800">
          Anything Counter
        </h1>
        {/* mt-4: 上方向のマージン（1rem） */}
        {/* text-gray-500: グレーのテキスト色 */}
        <p className="mt-4 text-gray-500">
          カウンターを追加して、毎日の習慣を記録しましょう。
        </p>
      </div>
    </div>
  );
}

// デフォルトエクスポート（main.tsxからインポートされる）
export default App;
```

### 実行・確認

```bash
# 開発サーバーを起動
$ npm run dev

# ブラウザで http://localhost:5173 にアクセス
# "Anything Counter" と "カウンターを追加して、毎日の習慣を記録しましょう。" が表示される
```

---

## 3-8. main.tsx の確認

### ファイル: `frontend/src/main.tsx`

#### このファイルの役割
Reactアプリケーションのエントリポイント。Viteが生成したものをそのまま使う。

#### コード（確認のみ、変更不要）

```tsx
// StrictMode: 開発時にReactの潜在的な問題を検出するラッパー
import { StrictMode } from "react";
// createRoot: React 18のルートAPI。DOMにReactツリーをマウントする
import { createRoot } from "react-dom/client";
// グローバルCSS（Tailwindのインポートを含む）
import "./index.css";
// ルートコンポーネント
import App from "./App.tsx";

// #root要素にReactアプリをマウント
// index.htmlの <div id="root"></div> に対応
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

---

## 3-9. 動作確認テスト

### 作成ファイル: `frontend/src/__tests__/App.test.tsx`

#### このファイルの役割
Appコンポーネントが正しくレンダリングされることを確認する最小テスト。

#### コード

```tsx
// render: Reactコンポーネントをテスト用のDOMにレンダリングする関数
// screen: レンダリングされたDOMを検索するユーティリティ
import { render, screen } from "@testing-library/react";
// テスト対象のコンポーネント
import App from "../App";

// describeブロック: テストをグループ化する
describe("App", () => {
  // it: テストケースを定義（testのエイリアス）
  it("タイトルが表示される", () => {
    // Appコンポーネントをレンダリング
    render(<App />);
    // "Anything Counter" というテキストが画面に存在することを確認
    // getByText: 指定テキストを含む要素を取得（見つからなければエラー）
    expect(screen.getByText("Anything Counter")).toBeInTheDocument();
  });
});
```

### 実行・確認

```bash
# テストを実行
$ npx vitest run

# 期待される出力:
# ✓ src/__tests__/App.test.tsx (1)
#   ✓ App (1)
#     ✓ タイトルが表示される
#
# Test Files  1 passed (1)
# Tests  1 passed (1)
```

---

## このステップのディレクトリ構造

```
frontend/
├── node_modules/              # npmパッケージ（gitignore対象）
├── package.json               # パッケージ定義
├── package-lock.json          # パッケージのロックファイル
├── tsconfig.json              # TypeScript設定（ルート）
├── tsconfig.app.json          # TypeScript設定（アプリ用）← types追加
├── tsconfig.node.json         # TypeScript設定（Node.js用）
├── vite.config.ts             # Vite設定 ← Tailwind + proxy + Vitest
├── index.html                 # HTMLエントリポイント
├── public/                    # 静的ファイル
├── src/
│   ├── main.tsx               # Reactエントリポイント
│   ├── index.css              # グローバルCSS ← Tailwindインポート
│   ├── App.tsx                # ルートコンポーネント ← プレースホルダー
│   ├── vite-env.d.ts          # Vite型定義（自動生成）
│   ├── types/
│   │   └── index.ts           # ← 新規: 型定義
│   ├── api/
│   │   └── client.ts          # ← 新規: APIクライアント
│   ├── test/
│   │   └── setup.ts           # ← 新規: テストセットアップ
│   └── __tests__/
│       └── App.test.tsx       # ← 新規: Appテスト
```

---

## このステップの完了チェックリスト

- [ ] `npm run dev` でVite開発サーバーが起動する（http://localhost:5173）
- [ ] ブラウザに "Anything Counter" が表示される
- [ ] Tailwind CSSのクラス（`bg-gray-50` など）が適用されている
- [ ] `npx tsc --noEmit` で型エラーがない
- [ ] `npx vitest run` でテストがパスする
- [ ] バックエンドを起動した状態で、ブラウザの開発者ツールから `fetch("/api/counters")` を実行してレスポンスが返る（プロキシ確認）
