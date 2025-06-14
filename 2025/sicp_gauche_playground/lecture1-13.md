🧠 目標

フィボナッチ数列 Fib(n) が以下の式で表せることを証明せよ：

Fib(n) = \frac{\varphi^n - \psi^n}{\sqrt{5}}
	•	\varphi = \frac{1 + \sqrt{5}}{2}（黄金比）
	•	\psi = \frac{1 - \sqrt{5}}{2}

⸻

🧩 アプローチ

1. フィボナッチ数列の定義（再掲）

Fib(0) = 0,\quad Fib(1) = 1,\quad Fib(n) = Fib(n-1) + Fib(n-2)

⸻

2. Binetの公式（証明すべき式）

Fib(n) = \frac{\varphi^n - \psi^n}{\sqrt{5}}

⸻

✅ Step 1: 初期条件の確認

n = 0

\frac{\varphi^0 - \psi^0}{\sqrt{5}} = \frac{1 - 1}{\sqrt{5}} = 0
\Rightarrow Fib(0)

n = 1

\frac{\varphi^1 - \psi^1}{\sqrt{5}} = \frac{\varphi - \psi}{\sqrt{5}} = \frac{\sqrt{5}}{\sqrt{5}} = 1
\Rightarrow Fib(1)

初期条件 OK ✅

⸻

✅ Step 2: 帰納法による証明

帰納法で次を仮定：

Fib(k) = \frac{\varphi^k - \psi^k}{\sqrt{5}},\quad Fib(k-1) = \frac{\varphi^{k-1} - \psi^{k-1}}{\sqrt{5}}

これを使って Fib(k+1) を示す：

Fib(k+1) = Fib(k) + Fib(k-1)

右辺を代入：

Fib(k+1) = \frac{\varphi^k - \psi^k}{\sqrt{5}} + \frac{\varphi^{k-1} - \psi^{k-1}}{\sqrt{5}} = \frac{\varphi^k + \varphi^{k-1} - (\psi^k + \psi^{k-1})}{\sqrt{5}}

ここで、φ, ψ は次の関係を持つ：

\varphi^k + \varphi^{k-1} = \varphi^{k+1},\quad \psi^k + \psi^{k-1} = \psi^{k+1}

※ これは φ, ψ の満たす2次方程式：
x^2 = x + 1
\Rightarrow x^{n+1} = x^n + x^{n-1}
から導かれる性質

したがって：

Fib(k+1) = \frac{\varphi^{k+1} - \psi^{k+1}}{\sqrt{5}}

よって帰納的に正しいことが示された ✅

⸻

✅ Step 3: Fib(n) が「φⁿ/√5 に最も近い整数」である理由
	•	ψ ≈ -0.618 で絶対値が 1 未満
	•	よって ψⁿ → 0（n が大きくなると）

すると：

Fib(n) = \frac{\varphi^n - \psi^n}{\sqrt{5}} ≈ \frac{\varphi^n}{\sqrt{5}}

ψⁿ/√5 は 0 < 1/2（絶対値）なので、Fib(n) は φⁿ/√5 に最も近い整数

⸻

✅ 結論まとめ
	•	フィボナッチ数列は閉じた式（Binetの公式）で表される
	•	その導出には φ, ψ が 2次方程式 x^2 = x + 1 の解であることを利用
	•	ψ の寄与が非常に小さいため、Fib(n) は φⁿ / √5 に最も近い整数となる

⸻

もしこの証明を Scheme で確認するコードも書きたければ、対応可能です！
