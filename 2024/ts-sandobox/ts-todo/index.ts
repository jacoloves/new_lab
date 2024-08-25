window.addEventListener('DOMContentLoaded', (event) => {
    const container: HTMLElement | null  = document.getElementById('container');
    const taskTable: HTMLTableElement | null = document.getElementById('taskTable') as HTMLTableElement;

    if (container && taskTable) {
        // create input element
        const input: HTMLInputElement = document.createElement('input');
        input.type = 'text';
        input.placeholder = 'Enter your name';

        container.appendChild(input);

        // create button element
        const button: HTMLButtonElement = document.createElement('button');
        button.textContent = 'Submit';

        container.appendChild(button);

        // create br element
        const br: HTMLBRElement = document.createElement('br');
        container.appendChild(br);

        // function to pad numbers with leading zeros
        const padNumber = (num: number, size: number): string => {
            let s = String(num);
            while(s.length < size) {
                s = '0' + s;
            }
            return s;
        };

        // function to start the stopwatch
        const startStopwatch = (stopwatch: HTMLSpanElement, intervalId: {id: number | null }) => {
            let minutes = 0;
            let seconds = 0;
            intervalId.id = window.setInterval(() => {
                seconds++;
                if (seconds === 60) {
                    seconds = 0;
                    minutes++;
                }
                stopwatch.textContent = `${padNumber(minutes, 2)}:${padNumber(seconds, 2)}`;
            }, 1000);
        };

        // function to stop the stopwatch
        const stopStopwatch =(intervalId: {id: number | null }) => {
            if (intervalId.id !== null) {
                clearInterval(intervalId.id);
                intervalId.id = null;
            }
        };

        // add envetn listner to button
        button.addEventListener('click', () => {
            const task: string | null = input.value.trim();
            if (task) {
                // create a new row
                const row: HTMLTableRowElement = taskTable.insertRow();

                // create a cell for the checkbox
                const cellCheckbox: HTMLTableCellElement = row.insertCell();
                const checkbox: HTMLInputElement = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.addEventListener('change', (event) => {
                    if (checkbox.checked) {
                       taskCell.style.textDecoration = 'line-through'; 
                    } else {
                        taskCell.style.textDecoration = 'none';
                    }
                });
                cellCheckbox.appendChild(checkbox);

                // create a cell for the task
                const taskCell: HTMLTableCellElement = row.insertCell();
                taskCell.textContent = task;

                // create a cell for the stopwatch
                const cellStopwatch: HTMLTableCellElement = row.insertCell();
                const stopwatch: HTMLSpanElement = document.createElement('span');
                stopwatch.textContent = '00:00';
                cellStopwatch.appendChild(stopwatch);

                // create a cell for the start button
                const cellStartButton: HTMLTableCellElement = row.insertCell();
                const startButton: HTMLButtonElement = document.createElement('button');
                startButton.textContent = 'Start';
                cellStartButton.appendChild(startButton);

                // create a cell for the stop button
                const cellStopButton: HTMLTableCellElement = row.insertCell();
                const stopButton: HTMLButtonElement = document.createElement('button');
                stopButton.textContent = 'Stop';
                stopButton.disabled = true;
                cellStopButton.appendChild(stopButton);

                // intervalId to keep track of the interval
                const intervalId: {id: number | null} = {id: null};

                // add event listener to start button
                startButton.addEventListener('click', () => {
                    startStopwatch(stopwatch, intervalId);
                    startButton.disabled = true;
                    stopButton.disabled = false;
                });

                // add event listener to stop button
                stopButton.addEventListener('click', () => {
                    stopStopwatch(intervalId);
                    startButton.disabled = false;
                    stopButton.disabled = true;
                });
                
                // clear input value
                input.value = '';
            } else {
                alert('Please enter a task');
            }
        });
    } else {
        console.error('Container not found');
    }
});