const buttonEl = document.createElement('button');
buttonEl.textContent = 'ボタン';

const div1El = document.querySelector('.container');
div1El.appendChild(buttonEl);

const h1El = document.getElementById('title');
const bodyEl = document.querySelector('body');

bodyEl.removeChild(h1El);
bodyEl.textContent = null;