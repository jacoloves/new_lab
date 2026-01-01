
const POINT_VALUES = [100, 150, 200, 300];
const STORAGE_KEY = 'sumNumber';

const init = () => {
  const container = document.getElementById('container');
  if (!container) return;

  container.replaceChildren();

  const title = document.createElement('h1');
  title.className = 'app-title';
  title.textContent = 'AtCoder Point Counter';

  const totalLabel = document.createElement('p');
  totalLabel.className = 'total-label';
  totalLabel.textContent = 'Total Points';

  const sumNum: HTMLParagraphElement = document.createElement('p');
  sumNum.id = 'sumNumber';
  sumNum.className = 'total-value';

  const savedValue = localStorage.getItem(STORAGE_KEY);
  sumNum.textContent = savedValue ?? '0';

  const addPoints = (point: number) => {
    const currentTotal = Number(sumNum.textContent ?? '0');
    const base = Number(currentTotal) ? currentTotal : 0;
    sumNum.textContent = String(base + point);
  };

  const grid = document.createElement('div');
  grid.className = 'point-grid';

  POINT_VALUES.forEach((value) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'point-button';
    button.textContent = value.toString();
    button.addEventListener('click', () => addPoints(value));
    grid.appendChild(button);
  });

  const actionRow = document.createElement('div');
  actionRow.className = 'action-row';

  const saveButton = document.createElement('button');
  saveButton.type = 'button';
  saveButton.className = 'action-button action-button--primary';
  saveButton.textContent = 'Save Total';
  saveButton.addEventListener('click', () => {
    localStorage.setItem(STORAGE_KEY, sumNum.textContent ?? '0');
  });

  const resetButton = document.createElement('button');
  resetButton.type = 'button';
  resetButton.className = 'action-button action-button--ghost action-button--danger';
  resetButton.textContent = 'Reset';
  resetButton.addEventListener('click', () => {
    sumNum.textContent = '0';
    localStorage.setItem(STORAGE_KEY, '0');
  });

  actionRow.append(saveButton, resetButton);
  container.append(title, totalLabel, sumNum, grid, actionRow);
};

document.addEventListener('DOMContentLoaded', init);
