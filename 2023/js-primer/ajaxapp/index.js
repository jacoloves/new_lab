const heading = document.querySelector("h2");

const headingText = heading.textContent;

const button = document.createElement("button");
button.textContent = "Push Me";

document.body.appendChild(button);

// const userId = "jacoloves";
function fetchUserInfo(userId) {
    fetch( `https://api.github.com/users/${encodeURIComponent(userId)}`)
        .then(response => {
            console.log(response.status);
            if (!response.ok) {
                console.error("error response", response);
            } else {
                return response.json().then(userInfo => {
                    console.log(userInfo);
                });
            }
        }).catch(error => {
            console.error(error);
        });
}