/* global variables */
// currnet date
const currentDate = new Date();
// title
const elmTitle: HTMLElement = document.querySelector('.cal__title')!;
// prev
const elmPrev: HTMLElement = document.querySelector('.cal__prev')!;
// next
const elmNext: HTMLElement = document.querySelector('.cal__next')!;
// days
const elmDays: HTMLElement = document.querySelector('.cal__days')!;

/* event handlers */
const onPageLoad = (): void => {
    updateView(currentDate);
}
const onPrev = (): void => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    updateView(currentDate);
}
const onNext = (): void => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    updateView(currentDate);
}

/* event listeners */
window.addEventListener('load', onPageLoad);
elmPrev.addEventListener('click', onPrev);
elmNext.addEventListener('click', onNext);

/* user defined functions */
function updateView(date: Date): void {
    updateTitle(date);
    updateDays(date);
}

function updateTitle(date: Date): void {
    const title: string = date.getFullYear().toString() + "年" + (date.getMonth() + 1).toString().padStart(2, "0") + "月";
    elmTitle.innerHTML = title;
}

function updateDays(date: Date): void {
    const dateList: number[] = [];
    const classList: string[] = [];

    const thisDays: number = getMonthDays(date);
    const prevDays: number = getFirstDayOfWeek(date);
    const prevLastDate: number = getPrevMonthDays(date);
    const rows: number = Math.ceil((thisDays + prevDays) / 7);

    for (let i: number = 0; i < rows * 7; i++) {
        if (i < prevDays) {
            dateList.push(prevLastDate - prevDays + i + 1);
            classList.push("cal__day cal__day--prev");
        } else if (prevDays <= i && i < prevDays + thisDays) {
            dateList.push(i - prevDays + 1);
            if (i % 7 === 0) {
                classList.push("cal__day cal__day--sun");
            } else if (i % 7 === 6) {
                classList.push("cal__day cal__day--sat");
            } else {
                classList.push("cal__day");
            }
        } else {
            dateList.push(i - (prevDays + thisDays) + 1);
            classList.push("cal__day cal__day--next");
        }
    }

    let html: string = "";

    for (let i: number = 0; i < rows*7; i++) {
        if (i % 7 === 0) {
            html += "<tr>";
        }
        html += '<td class="' + classList.shift() + '">' + dateList.shift()?.toString() + "</td>";
        if (i % 7 === 6) {
            html += "</tr>";
        }
    }

    elmDays.innerHTML = html;
}

function getMonthDays(date: Date): number {
    const lastDay: Date = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    lastDay.setMonth(lastDay.getMonth() + 1);
    lastDay.setDate(0);
    const days: number = lastDay.getDate();
    return days;
}

function getFirstDayOfWeek(date: Date): number {
    const firstDay: Date = new Date(date.getFullYear(), date.getMonth(), 1);
    const day: number = firstDay.getDay();
    return day;
}

function getPrevMonthDays(date: Date): number {
    const prevMonth: Date = new Date(date.getFullYear(), date.getMonth() - 1);
    const days: number = getMonthDays(prevMonth);
    return days;
}