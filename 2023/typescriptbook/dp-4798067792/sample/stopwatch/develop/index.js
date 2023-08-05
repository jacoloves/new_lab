/* Global variables */
let timeCount = 0;
let isRunning = false;
let timerID = 0;
const elmCount = document.querySelector('#count');
const elmStart = document.querySelector('#start');
const elmReset = document.querySelector('#reset');
/* event handler */
const onPageLoad = () => {
    updateView();
};
const onStart = () => {
    if (isRunning === false) {
        startTimer();
    }
    else {
        stopTimer();
    }
};
const onReset = () => {
    stopTimer();
    resetCount();
    updateView();
};
/* event listener */
window.addEventListener('load', onPageLoad);
elmStart.addEventListener('click', onStart);
elmReset.addEventListener('click', onReset);
/* user defined functions */
// update view
function updateView() {
    if (timeCount > 60 * 60 * 1000 - 1) {
        timeCount = 60 * 60 * 1000 - 1;
    }
    const mm = Math.floor(timeCount / 60000).toString().padStart(2, '0');
    const ss = (Math.floor(timeCount / 1000) % 60).toString().padStart(2, '0');
    const ms = (timeCount % 1000).toString().padStart(3, '0').slice(0, 2);
    const count = mm + ":" + ss + "<small>" + ms + "</small>";
    elmCount.innerHTML = count;
}
// start timer
function startTimer() {
    timerID = setInterval(() => {
        timeCount += 10;
        updateView();
    }, 10);
    isRunning = true;
}
// stop timer
function stopTimer() {
    clearInterval(timerID);
    isRunning = false;
}
// reset timer
function resetCount() {
    timeCount = 0;
}
