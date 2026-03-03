var POINT_VALUES = [100, 150, 200, 300];
var STORAGE_KEY = 'sumNumber';
var init = function () {
    var container = document.getElementById('container');
    if (!container)
        return;
    container.replaceChildren();
    var title = document.createElement('h1');
    title.className = 'app-title';
    title.textContent = 'AtCoder Point Counter';
    var totalLabel = document.createElement('p');
    totalLabel.className = 'total-label';
    totalLabel.textContent = 'Total Points';
    var sumNum = document.createElement('p');
    sumNum.id = 'sumNumber';
    sumNum.className = 'total-value';
    var savedValue = localStorage.getItem(STORAGE_KEY);
    sumNum.textContent = savedValue !== null && savedValue !== void 0 ? savedValue : '0';
    var addPoints = function (point) {
        var _a;
        var currentTotal = Number((_a = sumNum.textContent) !== null && _a !== void 0 ? _a : '0');
        var base = Number(currentTotal) ? currentTotal : 0;
        sumNum.textContent = String(base + point);
    };
    var grid = document.createElement('div');
    grid.className = 'point-grid';
    POINT_VALUES.forEach(function (value) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'point-button';
        button.textContent = value.toString();
        button.addEventListener('click', function () { return addPoints(value); });
        grid.appendChild(button);
    });
    var actionRow = document.createElement('div');
    actionRow.className = 'action-row';
    var saveButton = document.createElement('button');
    saveButton.type = 'button';
    saveButton.className = 'action-button action-button--primary';
    saveButton.textContent = 'Save Total';
    saveButton.addEventListener('click', function () {
        var _a;
        localStorage.setItem(STORAGE_KEY, (_a = sumNum.textContent) !== null && _a !== void 0 ? _a : '0');
    });
    var resetButton = document.createElement('button');
    resetButton.type = 'button';
    resetButton.className = 'action-button action-button--ghost action-button--danger';
    resetButton.textContent = 'Reset';
    resetButton.addEventListener('click', function () {
        sumNum.textContent = '0';
        localStorage.setItem(STORAGE_KEY, '0');
    });
    actionRow.append(saveButton, resetButton);
    container.append(title, totalLabel, sumNum, grid, actionRow);
};
document.addEventListener('DOMContentLoaded', init);
