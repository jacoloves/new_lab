const title1 = document.getElementById('title');
console.log(title1);

const title2 = document.querySelector("#title");
console.log(title2);

//const containers = document.getElementsByClassName('container');
//console.log(containers);

const container = document.querySelector('.container');
console.log(container);

const containers = document.querySelectorAll('.container');
console.log(containers);

const divEl = document.createElement('div');
console.log(divEl);

const nushidaEl = document.createElement('nushida');
console.log(nushidaEl);

const pEl = document.createElement('p');

/*
divEl.appendChild(pEl);
console.log(divEl);
*/

const h2El = document.createElement('h2');

divEl.appendChild(pEl);
divEl.appendChild(h2El);
console.log(divEl);
