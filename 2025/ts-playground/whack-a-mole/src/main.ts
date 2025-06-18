const app = document.querySelector<HTMLDivElement>('#app')!;

app.innerHTML = `
  <h1>🎯 Whack-a-Mole Game</h1>
  <div class="grid" id="game-board"></div>
`;

const board = document.getElementById('game-board')!;

for (let i = 0; i < 9; i++) {
  const square = document.createElement('div');
  square.classList.add('square');
  square.setAttribute('data-index', i.toString());
  square.textContent = '';
  board.appendChild(square);
}
