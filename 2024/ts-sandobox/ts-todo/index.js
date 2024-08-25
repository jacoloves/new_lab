window.addEventListener('DOMContentLoaded', function (event) {
    var container = document.getElementById('container');
    var taskTable = document.getElementById('taskTable');
    if (container && taskTable) {
        // create input element
        var input_1 = document.createElement('input');
        input_1.type = 'text';
        input_1.placeholder = 'Enter your name';
        container.appendChild(input_1);
        // create button element
        var button = document.createElement('button');
        button.textContent = 'Submit';
        container.appendChild(button);
        // create br element
        var br = document.createElement('br');
        container.appendChild(br);
        // function to pad numbers with leading zeros
        var padNumber_1 = function (num, size) {
            var s = String(num);
            while (s.length < size) {
                s = '0' + s;
            }
            return s;
        };
        // function to start the stopwatch
        var startStopwatch_1 = function (stopwatch, intervalId) {
            var minutes = 0;
            var seconds = 0;
            intervalId.id = window.setInterval(function () {
                seconds++;
                if (seconds === 60) {
                    seconds = 0;
                    minutes++;
                }
                stopwatch.textContent = "".concat(padNumber_1(minutes, 2), ":").concat(padNumber_1(seconds, 2));
            }, 1000);
        };
        // function to stop the stopwatch
        var stopStopwatch_1 = function (intervalId) {
            if (intervalId.id !== null) {
                clearInterval(intervalId.id);
                intervalId.id = null;
            }
        };
        // add envetn listner to button
        button.addEventListener('click', function () {
            var task = input_1.value.trim();
            if (task) {
                // create a new row
                var row = taskTable.insertRow();
                // create a cell for the checkbox
                var cellCheckbox = row.insertCell();
                var checkbox_1 = document.createElement('input');
                checkbox_1.type = 'checkbox';
                checkbox_1.addEventListener('change', function (event) {
                    if (checkbox_1.checked) {
                        taskCell_1.style.textDecoration = 'line-through';
                    }
                    else {
                        taskCell_1.style.textDecoration = 'none';
                    }
                });
                cellCheckbox.appendChild(checkbox_1);
                // create a cell for the task
                var taskCell_1 = row.insertCell();
                taskCell_1.textContent = task;
                // create a cell for the stopwatch
                var cellStopwatch = row.insertCell();
                var stopwatch_1 = document.createElement('span');
                stopwatch_1.textContent = '00:00';
                cellStopwatch.appendChild(stopwatch_1);
                // create a cell for the start button
                var cellStartButton = row.insertCell();
                var startButton_1 = document.createElement('button');
                startButton_1.textContent = 'Start';
                cellStartButton.appendChild(startButton_1);
                // create a cell for the stop button
                var cellStopButton = row.insertCell();
                var stopButton_1 = document.createElement('button');
                stopButton_1.textContent = 'Stop';
                stopButton_1.disabled = true;
                cellStopButton.appendChild(stopButton_1);
                // intervalId to keep track of the interval
                var intervalId_1 = { id: null };
                // add event listener to start button
                startButton_1.addEventListener('click', function () {
                    startStopwatch_1(stopwatch_1, intervalId_1);
                    startButton_1.disabled = true;
                    stopButton_1.disabled = false;
                });
                // add event listener to stop button
                stopButton_1.addEventListener('click', function () {
                    stopStopwatch_1(intervalId_1);
                    startButton_1.disabled = false;
                    stopButton_1.disabled = true;
                });
                // clear input value
                input_1.value = '';
            }
            else {
                alert('Please enter a task');
            }
        });
    }
    else {
        console.error('Container not found');
    }
});
