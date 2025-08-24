class NumberGuessingGame {
  private targetNumber: number;
  private attempts: number;
  private gameOver: boolean;
  private guessHistory: Array<{guess: number, hint: string}>;
  private readonly MIN_NUMBER = 1;
  private readonly MAX_NUMBER = 100;

  // DOM elements
  private guessInput: HTMLInputElement;
  private guessButton: HTMLButtonElement;
  private newGameButton: HTMLButtonElement;
  private message: HTMLElement;
  private attemptCount: HTMLElement;
  private historyContainer: HTMLElement;
  private historyList: HTMLElement;

  constructor() {
    this.initializeElements();
    this.setupEventListeners();
    this.startNewGame();
  }

  private initializeElements(): void {
    this.guessInput = document.getElementById('guessInput') as HTMLInputElement;
    this.guessButton = document.getElementById('guessButton') as HTMLButtonElement;
    this.newGameButton = document.getElementById('newGameButton') as HTMLButtonElement;
    this.message = document.getElementById('message') as HTMLElement;
    this.attemptCount = document.getElementById('attemptCount') as HTMLElement;
    this.historyContainer = document.getElementById('historyContainer') as HTMLElement;
    this.historyList = document.getElementById('historyList') as HTMLElement;
  }

  private setupEventListeners(): void {
    this.guessButton.addEventListener('click', () => this.makeGuess());
    this.newGameButton.addEventListener('click', () => this.startNewGame());

    this.guessInput.addEventListener('keypress', (e: KeyboardEvent) => {
      if (e.key === 'Enter') {
        this.makeGuess();
      }
    });

    this.guessInput.addEventListener('input', () => {
      const value = parseInt(this.guessInput.value);
      if (value < this.MIN_NUMBER || value > this.MAX_NUMBER) {
        this.guessInput.style.borderColor = '#dc3545';
      } else {
        this.guessInput.style.borderColor = '';
      }
    });
  }

  private startNewGame(): void {
    this.targetNumber = Math.floor(Math.random() * this.MAX_NUMBER) + this.MIN_NUMBER;
    this.attempts = 0;
    this.gameOver = false;
    this.guessHistory = [];

    this.updateUI();
    this.showMessage('1から100までの数字を当ててください!', '');
    this.guessInput.disabled = false;
    this.guessButton.disabled = false;
    this.guessInput.focus();
    this.historyContainer.style.display = 'none';

    console.log('🎯 新しいゲーム開始!正解: ${this.targetNumber}');
  }

  private makeGuess(): void {
    if (this.gameOver) return;

  const guess = parseInt(this.guessInput.value);

    if (isNaN(guess) || guess < this.MIN_NUMBER || guess > this.MAX_NUMBER) {
      this.showMessage('から100までの数字を入力してください', 'error');
      return;
    }

    this.attempts++;
    this.updateUI();

    const result = this.checkGuess(guess);
    this.guessHistory.push({ guess, hint: result.message });
    this.updateHistory();

    if (result.correct) {
      this.gameOver = true;
      this.showMessage(result.message, 'success');
      this.guessInput.disabled = true;
      this.guessButton.disabled = true;
      this.historyContainer.style.display = 'block';
    } else {
      this.showMessage(result.message, 'hint');
    }

    this.guessInput.value = '';
    this.guessInput.focus();
  }

  private checkGuess(guess: number): {correct: boolean, message: string} {
    if (guess === this.targetNumber) {
      const performance = this.getPerformanceMessage();
      return {
        correct: true,
        message: `🎉 正解! ${this.attempts}回で当てました! ${performance}`
      };
    } else if (guess < this.targetNumber) {
      const hint = this.getDetailedHint(guess, this.targetNumber);
      return {
        correct: false,
        message: `📈 もっと大きい数字です ${hint}`
      };
    } else {
      const hint = this.getDetailedHint(guess, this.targetNumber);
      return {
        correct: false,
        message: `📉 もっと小さい数字です ${hint}`
      }
    }
  }

  private getDetailedHint(guess: number, target: number): string {
    const difference = Math.abs(guess - target);
    if (difference <= 5) return '(かなり近い！)';
    if (difference <= 10) return '(近い！)';
    if (difference <= 20) return '(そこそこ近い！)';
    return '(まだ遠い)';
  }

  private getPerformanceMessage(): string {
    if (this.attempts <= 3) return ' 素晴らしい！';
    if (this.attempts <= 6) return ' いいですね！';
    if (this.attempts <= 10) return ' よく頑張りました！';
    return ' お疲れ様でした！';
  }

  private showMessage(text: string, type: string): void {
    this.message.textContent = text;
    this.message.className = `message ${type}`;
  }

  private updateUI(): void {
    this.attemptCount.textContent = this.attempts.toString();
  }

  private updateHistory(): void {
    this.historyList.innerHTML = '';
    this.guessHistory.forEach((item, index) => {
      const div = document.createElement('div');
      div.className = 'guess-item';
      div.innerHTML = `
        <span>${index + 1}回目: ${item.guess}</span>
        <span>${item.hint}</span>
      `;
      this.historyList.appendChild(div);
    });
    this.historyContainer.style.display = 'block';
  }
}

// Game Start
new NumberGuessingGame();
