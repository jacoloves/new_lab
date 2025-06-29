const app = document.querySelector<HTMLDivElement>('#app')!;

app.innerHTML = `
  <h1>🎯 Whack-a-Mole Game</h1>
  <p>Score: <span id="score">0</span></p>
  <p>Time Left: <span id="timer">30</span>s</p>
  <div class="grid" id="game-board"></div>
  <p id="game-over" style="font-weight: bold; font-size: 1.2rem; color: red;"></p>
`;

const board = document.getElementById('game-board')!;
const scoreDisplay = document.getElementById('score')!;
const timerDisplay = document.getElementById('timer')!;
const gameOverDisplay = document.getElementById('game-over')!;

let score = 0;
let timeLeft = 30;
let currentMoleIndex: number | null = null;

for (let i = 0; i < 9; i++) {
  const square = document.createElement('div');
  square.classList.add('square');
  square.setAttribute('data-index', i.toString());
  board.appendChild(square);
}

const squares = document.querySelectorAll<HTMLDivElement>('.square');

function showRandomMole() {
  squares.forEach((sq) => (sq.textContent = ''));

  const index = Math.floor(Math.random() * squares.length);
  squares[index].textContent = '🐹';
  currentMoleIndex = index;
}

squares.forEach((square, i) => {
  square.addEventListener('click', () => {
    if (i === currentMoleIndex) {
      score += 1;
      scoreDisplay.textContent = score.toString();
      square.textContent = '';
      currentMoleIndex = null;
    }
  });
});

setInterval(showRandomMole, 1000);
