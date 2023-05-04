export function escapeSpecialChars(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&qout;")
        .replace(/'/g, "&#039;");
}

/**
 * HTML string => HTML element
 * @param {string} html
 */
export function htmlToElement(html) {
    const template = document.createElement("template");
    template.innerHTML = html;
    return template.content.firstElementChild;
}

/**
 * @return {Element}
 */
export function element(strings, ...values) {
    const htmlString = strings.reduce((result, str, i) => {
        const value = values[i-1];
        if (typeof value === "string") {
            return result + escapeSpecialChars(value) + str;
        } else{
            return result + String(value) + str;
        }
    });
    return htmlToElement(htmlString);
}


/**
 * @param {Element} bodyElement
 * @param {Element} containerElement
 */
export function render(bodyElement, containerElement) {
    containerElement.innerHTML = "";
    containerElement.appendChild(bodyElement);
}
