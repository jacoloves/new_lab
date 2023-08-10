/* global variables */
// currnet date
const currentDate = new Date();
// title
const elmTitle = document.querySelector('.cal__title');
// prev
const elmPrev = document.querySelector('.cal__prev');
// next
const elmNext = document.querySelector('.cal__next');
// days
const elmDays = document.querySelector('.cal__days');
/* event handlers */
const onPageLoad = () => {
    updateView(currentDate);
};
const onPrev = () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    updateView(currentDate);
};
const onNext = () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    updateView(currentDate);
};
/* event listeners */
window.addEventListener('load', onPageLoad);
elmPrev.addEventListener('click', onPrev);
elmNext.addEventListener('click', onNext);
/* user defined functions */
function updateView(date) {
    updateTitle(date);
    updateDays(date);
}
function updateTitle(date) {
    const title = date.getFullYear().toString() + "年" + (date.getMonth() + 1).toString().padStart(2, "0") + "月";
    elmTitle.innerHTML = title;
}
function updateDays(date) {
    const dateList = [];
    const classList = [];
    const thisDays = getMonthDays(date);
    const prevDays = getFirstDayOfWeek(date);
    const prevLastDate = getPrevMonthDays(date);
    const rows = Math.ceil((thisDays + prevDays) / 7);
    for (let i = 0; i < rows * 7; i++) {
        if (i < prevDays) {
            dateList.push(prevLastDate - prevDays + i + 1);
            classList.push("cal__day cal__day--prev");
        }
        else if (prevDays <= i && i < prevDays + thisDays) {
            dateList.push(i - prevDays + 1);
            if (i % 7 === 0) {
                classList.push("cal__day cal__day--sun");
            }
            else if (i % 7 === 6) {
                classList.push("cal__day cal__day--sat");
            }
            else {
                classList.push("cal__day");
            }
        }
        else {
            dateList.push(i - (prevDays + thisDays) + 1);
            classList.push("cal__day cal__day--next");
        }
    }
    let html = "";
    for (let i = 0; i < rows * 7; i++) {
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
function getMonthDays(date) {
    const lastDay = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    lastDay.setMonth(lastDay.getMonth() + 1);
    lastDay.setDate(0);
    const days = lastDay.getDate();
    return days;
}
function getFirstDayOfWeek(date) {
    const firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
    const day = firstDay.getDay();
    return day;
}
function getPrevMonthDays(date) {
    const prevMonth = new Date(date.getFullYear(), date.getMonth() - 1);
    const days = getMonthDays(prevMonth);
    return days;
}
