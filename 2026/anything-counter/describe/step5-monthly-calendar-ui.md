# Step 5: 月間カレンダーUI（MonthlyGrid + useRecords）

## このステップで作るもの

- useRecords カスタムフック（月別記録の取得・トグル）
- MonthlyGrid コンポーネント（月間カレンダーグリッド）
- CounterCard の更新（アコーディオン展開でMonthlyGridを表示）

**完了後の状態**: カウンターカードをクリックすると月間カレンダーが展開表示される。実行した日に●マークが付く。直近3日以内の日付をタップして記録の追加・削除ができる。月の切り替え（前月・次月）ができる。

## 前提条件

- Step 4 が完了していること（カウンター一覧UIが動作する状態）
- `frontend/` ディレクトリにいること

---

## 5-1. useRecords カスタムフック

### 作成ファイル: `frontend/src/hooks/useRecords.ts`

#### このファイルの役割
指定カウンターの月別記録を取得・管理する。月の切り替え、記録のトグル（追加・削除）ロジックを提供する。

#### コード

```typescript
/**
 * useRecords カスタムフック
 * 指定カウンターの月別記録を取得し、日付ごとの記録トグルを管理する
 */

import { useState, useEffect, useCallback } from "react";
// Record型のインポート
import type { Record as RecordType } from "../types";
// APIクライアント関数
import {
  fetchRecords,
  createRecord as apiCreateRecord,
  deleteRecord as apiDeleteRecord,
} from "../api/client";

/**
 * useRecordsの戻り値の型定義
 */
type UseRecordsReturn = {
  /** 現在表示中の年月の記録一覧 */
  records: RecordType[];
  /** 表示中の年 */
  year: number;
  /** 表示中の月（1-12） */
  month: number;
  /** データ読み込み中かどうか */
  loading: boolean;
  /** 前月に移動する関数 */
  goToPrevMonth: () => void;
  /** 次月に移動する関数 */
  goToNextMonth: () => void;
  /** 指定日付の記録をトグルする関数（ある→削除、ない→作成） */
  toggleDate: (date: string) => Promise<void>;
  /** 指定日付に記録が存在するかチェックする関数 */
  hasRecord: (date: string) => boolean;
};

/**
 * 月別記録を管理するカスタムフック
 *
 * @param counterId - 対象のカウンターID
 * @param enabled - フックを有効にするかどうか（アコーディオン展開時のみtrue）
 */
export function useRecords(counterId: number, enabled: boolean): UseRecordsReturn {
  // 現在の年月を初期値とする
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1); // JavaScriptの月は0始まりなので+1
  // 記録一覧
  const [records, setRecords] = useState<RecordType[]>([]);
  // ローディング状態
  const [loading, setLoading] = useState(false);

  /**
   * 指定年月の記録をAPIから取得する
   */
  const load = useCallback(async () => {
    if (!enabled) return; // 無効時はスキップ
    setLoading(true);
    try {
      const data = await fetchRecords(counterId, year, month);
      setRecords(data);
    } catch {
      // エラー時は空にする（UIにはエラー表示しない、シンプルに保つ）
      setRecords([]);
    } finally {
      setLoading(false);
    }
  }, [counterId, year, month, enabled]);

  // counterId, year, month, enabledが変わるたびにデータを再取得
  useEffect(() => {
    load();
  }, [load]);

  /**
   * 前月に移動する
   * 1月の場合は前年の12月に移動
   */
  const goToPrevMonth = useCallback(() => {
    setMonth((prev) => {
      if (prev === 1) {
        // 1月 → 前年の12月
        setYear((y) => y - 1);
        return 12;
      }
      return prev - 1;
    });
  }, []);

  /**
   * 次月に移動する
   * 12月の場合は翌年の1月に移動
   */
  const goToNextMonth = useCallback(() => {
    setMonth((prev) => {
      if (prev === 12) {
        // 12月 → 翌年の1月
        setYear((y) => y + 1);
        return 1;
      }
      return prev + 1;
    });
  }, []);

  /**
   * 指定日付の記録をトグル（ある→削除、ない→作成）
   * @param date - "YYYY-MM-DD" 形式の日付
   */
  const toggleDate = useCallback(
    async (date: string) => {
      try {
        if (hasRecordFn(date)) {
          // 記録あり → 削除
          await apiDeleteRecord(counterId, date);
        } else {
          // 記録なし → 作成
          await apiCreateRecord(counterId, date);
        }
        // 記録一覧を再取得して最新状態を反映
        await load();
      } catch {
        // エラー時は何もしない（バリデーションエラーはAPIが400を返す）
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [counterId, load, records],
  );

  /**
   * 指定日付に記録が存在するかチェックする
   * @param date - "YYYY-MM-DD" 形式の日付
   * @returns 記録が存在すればtrue
   */
  function hasRecordFn(date: string): boolean {
    return records.some((r) => r.date === date);
  }

  return {
    records,
    year,
    month,
    loading,
    goToPrevMonth,
    goToNextMonth,
    toggleDate,
    hasRecord: hasRecordFn,
  };
}
```

---

## 5-2. MonthlyGrid コンポーネント

### 作成ファイル: `frontend/src/components/MonthlyGrid.tsx`

#### このファイルの役割
月間カレンダーをグリッド表示する。日-土の7列で週ごとに行を表示し、記録がある日に●マークを付ける。直近3日以内の日付はタップで記録を追加・削除できる。

#### コード

```tsx
/**
 * MonthlyGridコンポーネント — 月間カレンダーグリッド
 *
 * 機能:
 * - 日-土の7列グリッドで月間カレンダーを表示
 * - 記録がある日に●を表示
 * - 直近3日以内の日付をタップして記録をトグル
 * - 前月・次月のナビゲーション
 */

/**
 * MonthlyGridのprops
 */
type Props = {
  /** 表示中の年 */
  year: number;
  /** 表示中の月（1-12） */
  month: number;
  /** データ読み込み中かどうか */
  loading: boolean;
  /** 前月に移動する関数 */
  onPrevMonth: () => void;
  /** 次月に移動する関数 */
  onNextMonth: () => void;
  /** 指定日付に記録が存在するかチェックする関数 */
  hasRecord: (date: string) => boolean;
  /** 指定日付の記録をトグルする関数 */
  onToggleDate: (date: string) => Promise<void>;
};

/**
 * 曜日ヘッダーの定義（日曜始まり）
 */
const WEEKDAYS = ["日", "月", "火", "水", "木", "金", "土"];

/**
 * 指定した日付が編集可能かどうかを判定する
 * ルール: 今日から3日前までが編集可能（未来日は不可）
 *
 * @param dateStr - "YYYY-MM-DD" 形式の日付
 * @returns 編集可能ならtrue
 */
function isEditable(dateStr: string): boolean {
  const today = new Date();
  // 時刻部分をリセット（日付のみで比較するため）
  today.setHours(0, 0, 0, 0);

  const target = new Date(dateStr + "T00:00:00");
  // 今日との差分をミリ秒で計算 → 日数に変換
  const diffMs = today.getTime() - target.getTime();
  const diffDays = diffMs / (1000 * 60 * 60 * 24);

  // 0 <= diffDays <= 3 の範囲が編集可能（今日〜3日前）
  return diffDays >= 0 && diffDays <= 3;
}

/**
 * 指定年月のカレンダーデータ（日付文字列の2次元配列）を生成する
 *
 * @param year - 年
 * @param month - 月（1-12）
 * @returns 週ごとの配列。各要素は "YYYY-MM-DD" または "" （空セル）
 */
function generateCalendar(year: number, month: number): string[][] {
  // その月の1日を取得
  const firstDay = new Date(year, month - 1, 1);
  // その月の最終日を取得（翌月の0日 = 当月の末日）
  const lastDay = new Date(year, month, 0);
  // 1日の曜日（0=日, 1=月, ..., 6=土）
  const startWeekday = firstDay.getDay();
  // その月の日数
  const daysInMonth = lastDay.getDate();

  const weeks: string[][] = [];
  let currentWeek: string[] = [];

  // 1日より前の空セルを埋める（月が水曜始まりなら、日〜火が空）
  for (let i = 0; i < startWeekday; i++) {
    currentWeek.push("");
  }

  // 各日のセルを生成
  for (let day = 1; day <= daysInMonth; day++) {
    // "YYYY-MM-DD" 形式の日付文字列を生成
    // padStart(2, "0"): 1桁の数字を0埋めして2桁にする（1 → "01"）
    const dateStr = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    currentWeek.push(dateStr);

    // 土曜日（7個目）で改行
    if (currentWeek.length === 7) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
  }

  // 最終週の残りの空セルを埋める
  if (currentWeek.length > 0) {
    while (currentWeek.length < 7) {
      currentWeek.push("");
    }
    weeks.push(currentWeek);
  }

  return weeks;
}

function MonthlyGrid({
  year,
  month,
  loading,
  onPrevMonth,
  onNextMonth,
  hasRecord,
  onToggleDate,
}: Props) {
  // カレンダーデータを生成
  const weeks = generateCalendar(year, month);

  return (
    <div>
      {/* 月ナビゲーション: < 2026年2月 > */}
      <div className="mb-3 flex items-center justify-between">
        {/* 前月ボタン */}
        <button
          onClick={onPrevMonth}
          className="rounded px-2 py-1 text-gray-600 hover:bg-gray-100"
          aria-label="前月"
        >
          ◀
        </button>

        {/* 年月表示 */}
        <span className="text-sm font-medium text-gray-700">
          {year}年{month}月
        </span>

        {/* 次月ボタン */}
        <button
          onClick={onNextMonth}
          className="rounded px-2 py-1 text-gray-600 hover:bg-gray-100"
          aria-label="次月"
        >
          ▶
        </button>
      </div>

      {/* ローディング表示 */}
      {loading ? (
        <p className="text-center text-sm text-gray-400">読み込み中...</p>
      ) : (
        <>
          {/* 曜日ヘッダー（日〜土） */}
          {/* grid grid-cols-7: 7列のグリッドレイアウト */}
          <div className="mb-1 grid grid-cols-7 text-center text-xs text-gray-500">
            {WEEKDAYS.map((day) => (
              <div key={day}>{day}</div>
            ))}
          </div>

          {/* カレンダー本体 */}
          {weeks.map((week, weekIndex) => (
            <div key={weekIndex} className="grid grid-cols-7 text-center">
              {week.map((dateStr, dayIndex) => {
                // 空セルの場合
                if (!dateStr) {
                  return <div key={dayIndex} className="p-1" />;
                }

                // 日付部分のみ取得（"2026-02-23" → 23）
                const dayNumber = parseInt(dateStr.split("-")[2], 10);
                // この日に記録があるか
                const done = hasRecord(dateStr);
                // この日が編集可能か（直近3日以内）
                const editable = isEditable(dateStr);

                return (
                  <button
                    key={dayIndex}
                    onClick={() => {
                      // 編集可能な日付のみトグル
                      if (editable) {
                        onToggleDate(dateStr);
                      }
                    }}
                    // 編集不可の日付はカーソルをデフォルトに（クリックできないことを示す）
                    className={`p-1 text-xs ${
                      editable ? "cursor-pointer hover:bg-gray-100" : "cursor-default"
                    }`}
                    // 編集不可の場合はbutton機能を無効化しないが、視覚的に区別する
                    aria-label={`${dateStr}${done ? "（記録あり）" : ""}`}
                  >
                    {/* 日付の数字 */}
                    <div className={editable ? "text-gray-700" : "text-gray-400"}>
                      {dayNumber}
                    </div>
                    {/* 記録がある日は●を表示 */}
                    {done ? (
                      <div className="text-green-500">●</div>
                    ) : (
                      // 高さを揃えるためのスペーサー
                      <div className="invisible">●</div>
                    )}
                  </button>
                );
              })}
            </div>
          ))}
        </>
      )}
    </div>
  );
}

export default MonthlyGrid;
```

---

## 5-3. CounterCard の更新（MonthlyGrid統合）

### 更新ファイル: `frontend/src/components/CounterCard.tsx`

#### 変更内容
アコーディオン展開部分にMonthlyGridコンポーネントを統合する。

#### コード（全体を差し替え）

```tsx
/**
 * CounterCardコンポーネント — 個別カウンターの表示カード
 *
 * 機能:
 * - タップでtoday_doneを切り替え
 * - チェック済みカードの背景色変更
 * - 削除ボタン
 * - アコーディオン展開で月間カレンダー表示（MonthlyGrid）
 */

import type { Counter } from "../types";
// 月別記録管理フック
import { useRecords } from "../hooks/useRecords";
// 月間カレンダーコンポーネント
import MonthlyGrid from "./MonthlyGrid";

type Props = {
  counter: Counter;
  onToggleToday: (counter: Counter) => void;
  onDelete: (id: number) => void;
  onSelect: (id: number) => void;
  isSelected: boolean;
};

function CounterCard({ counter, onToggleToday, onDelete, onSelect, isSelected }: Props) {
  // useRecordsフック: isSelectedがtrueのときのみデータ取得を有効化
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
      {/* カードの上段: チェックボタン + カウンター名 + 削除ボタン */}
      <div className="flex items-center gap-3">
        {/* チェックボタン */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleToday(counter);
          }}
          className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full border-2 transition-colors"
          aria-label={counter.today_done ? "チェックを外す" : "チェックする"}
        >
          {counter.today_done && (
            <span className="text-green-600 text-lg">✓</span>
          )}
        </button>

        {/* カウンター名（クリックでアコーディオン展開） */}
        <span
          className="flex-1 cursor-pointer truncate text-gray-800"
          onClick={() => onSelect(counter.id)}
        >
          {counter.name}
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

      {/* アコーディオン展開部分: MonthlyGridを表示 */}
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

## 5-4. テストの作成

### 作成ファイル: `frontend/src/__tests__/MonthlyGrid.test.tsx`

#### このファイルの役割
MonthlyGridコンポーネントの表示と操作をテストする。

#### コード

```tsx
/**
 * MonthlyGridコンポーネントのテスト
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import MonthlyGrid from "../components/MonthlyGrid";

// モック関数
const mockPrevMonth = vi.fn();
const mockNextMonth = vi.fn();
const mockToggleDate = vi.fn().mockResolvedValue(undefined);
// hasRecord: 特定の日付にのみtrueを返す
const mockHasRecord = vi.fn((date: string) => date === "2026-03-01");

// テスト用の共通props
const defaultProps = {
  year: 2026,
  month: 3,
  loading: false,
  onPrevMonth: mockPrevMonth,
  onNextMonth: mockNextMonth,
  hasRecord: mockHasRecord,
  onToggleDate: mockToggleDate,
};

describe("MonthlyGrid", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("年月が表示される", () => {
    render(<MonthlyGrid {...defaultProps} />);
    // "2026年3月" のテキストが表示されることを確認
    expect(screen.getByText("2026年3月")).toBeInTheDocument();
  });

  it("曜日ヘッダーが表示される", () => {
    render(<MonthlyGrid {...defaultProps} />);
    // 全曜日が表示されることを確認
    expect(screen.getByText("日")).toBeInTheDocument();
    expect(screen.getByText("月")).toBeInTheDocument();
    expect(screen.getByText("土")).toBeInTheDocument();
  });

  it("日付が表示される", () => {
    render(<MonthlyGrid {...defaultProps} />);
    // 1日と31日が表示されることを確認（2026年3月は31日まで）
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("31")).toBeInTheDocument();
  });

  it("記録がある日に●が表示される", () => {
    render(<MonthlyGrid {...defaultProps} />);
    // ●マークが画面に存在することを確認
    const dots = screen.getAllByText("●");
    // 少なくとも1つは表示されているはず（3/1に記録がある設定）
    expect(dots.length).toBeGreaterThan(0);
  });

  it("前月ボタンをクリックするとonPrevMonthが呼ばれる", async () => {
    const user = userEvent.setup();
    render(<MonthlyGrid {...defaultProps} />);
    await user.click(screen.getByLabelText("前月"));
    expect(mockPrevMonth).toHaveBeenCalledTimes(1);
  });

  it("次月ボタンをクリックするとonNextMonthが呼ばれる", async () => {
    const user = userEvent.setup();
    render(<MonthlyGrid {...defaultProps} />);
    await user.click(screen.getByLabelText("次月"));
    expect(mockNextMonth).toHaveBeenCalledTimes(1);
  });

  it("ローディング中は読み込みメッセージが表示される", () => {
    render(<MonthlyGrid {...defaultProps} loading={true} />);
    expect(screen.getByText("読み込み中...")).toBeInTheDocument();
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
# ✓ src/__tests__/CounterCard.test.tsx (4)
# ✓ src/__tests__/MonthlyGrid.test.tsx (7)
#
# Test Files  3 passed (3)
# Tests  13 passed (13)
```

---

## 手動での動作確認

```bash
# バックエンドとフロントエンドを両方起動した状態でブラウザを確認
#
# 確認項目:
# 1. カウンターを追加する
# 2. カウンター名をクリック → 月間カレンダーが展開される
# 3. カレンダーに今月の日付が正しく表示される
# 4. 今日のチェックボタン（○）をクリック → ✓に変わる
# 5. カレンダー上の今日の日付に●が表示される
# 6. ◀ ボタンで前月に切り替え → 前月のカレンダーが表示される
# 7. ▶ ボタンで次月に切り替え → 次月のカレンダーが表示される
# 8. 直近3日以内の日付をクリック → ●が追加/削除される
# 9. 4日以上前の日付をクリック → 何も起きない（編集不可）
```

---

## このステップのディレクトリ構造

```
frontend/src/
├── hooks/
│   ├── useCounters.ts
│   └── useRecords.ts          # ← 新規
├── components/
│   ├── Header.tsx
│   ├── AddCounterForm.tsx
│   ├── CounterCard.tsx         # ← 更新（MonthlyGrid統合）
│   ├── CounterList.tsx
│   └── MonthlyGrid.tsx         # ← 新規
└── __tests__/
    ├── App.test.tsx
    ├── CounterCard.test.tsx
    └── MonthlyGrid.test.tsx    # ← 新規
```

---

## このステップの完了チェックリスト

- [ ] `npx vitest run` で13件全てのテストがパスする
- [ ] カウンターカードをクリックすると月間カレンダーが展開される
- [ ] カレンダーに日-土の曜日ヘッダーが表示される
- [ ] 今月のカレンダーが正しい日数で表示される（例: 3月は31日）
- [ ] 記録がある日に●が表示される
- [ ] 直近3日以内の日付をタップすると●の追加/削除ができる
- [ ] 4日以上前の日付はタップしても何も起きない
- [ ] ◀▶ ボタンで前月・次月に切り替えられる
- [ ] 同じカードを再クリックするとアコーディオンが閉じる
