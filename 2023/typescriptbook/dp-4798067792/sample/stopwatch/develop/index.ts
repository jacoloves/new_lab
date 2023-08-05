/* Global variables */
let timeCount: number = 0;
let isRunning: boolean = false;
let timerID: number = 0;
const elmCount: HTMLElement = document.querySelector('#count')!;
const elmStart: HTMLElement = document.querySelector('#start')!;
const elmReset: HTMLElement = document.querySelector('#reset')!;

/* event handler */
const onPageLoad = () => {
    updateView();
};

const onStart = () => {
    if (isRunning === false) {
        startTimer();
    } else {
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
    const mm: string = Math.floor(timeCount / 60000).toString().padStart(2, '0');
    const ss: string = (Math.floor(timeCount / 1000) % 60).toString().padStart(2, '0');
    const ms: string = (timeCount % 1000).toString().padStart(3, '0').slice(0, 2);
    const count: string = mm + ":" + ss + "<small>" + ms + "</small>";
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