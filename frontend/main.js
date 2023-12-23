document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const apiKey = document.getElementById('apiKey').value;
    validateUser(username, apiKey);
});

function validateUser(username, apiKey) {
    fetch('http://localhost:5000/api/validate-user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username, api_key: apiKey })
    })
    .then(response => response.json())
    .then(data => handleLoginResponse(data))
    .catch(error => console.error('Error when validating you:', error));
}

function handleLoginResponse(data) {
    if (data.valid) {
        localStorage.setItem('apiKey', data.api_key);
        document.getElementById('loginForm').classList.add('d-none');
        document.getElementById('psalmSelection').classList.remove('d-none');
        loadPsalms();
    } else {
        document.getElementById('loginError').innerText = "Who are you? I don't know you";
        document.getElementById('loginError').classList.remove('d-none');
    }
}

function loadPsalms() {
    const apiKey = localStorage.getItem('apiKey');
    fetch('http://localhost:5000/api/psalms', {
        headers: {
            'X-API-KEY': apiKey
        }
    })
    .then(response => response.json())
    .then(psalms => {
        const psalmButtonsContainer = document.getElementById('psalmButtons');
        psalmButtonsContainer.innerHTML = ''; // just in case any are left over
        psalms.forEach(psalm => {
            const button = document.createElement('button');
            button.className = 'btn btn-outline-primary m-1';
            button.textContent = `${psalm.number}`
            button.onclick = () => loadPsalmDetails(psalm.number);
            psalmButtonsContainer.appendChild(button);
        });
    }).catch(error => console.error('I am not good at loading psalms, excuuuuse me:', error));
}

function loadPsalmDetails(psalmNumber) {
    const apiKey = localStorage.getItem('apiKey');
    fetch(`http://localhost:5000/api/psalms/${psalmNumber}`, {
        headers: {
            'X-API-KEY': apiKey
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(psalmDetails => {
        displayPsalmDetails(psalmDetails);
    })
    .catch(error => {
        console.error('I dropped the psalm details:', error);
        // maybe redirect to the search page? not sure what I will do in this case
    });
}


document.getElementById('logoHome').addEventListener('click', function(event) {
    event.preventDefault();
    document.getElementById('psalmSelection').classList.remove('d-none');
    document.getElementById('psalmDisplay').classList.add('d-none');
});



function displayPsalmDetails(psalmDetails) {
    const psalmDisplayDiv = document.getElementById('psalmDisplay');
    const psalmContentDiv = document.getElementById('psalmContent');
    // out with the old
    psalmContentDiv.innerHTML = '';
    document.getElementById('psalmSelection').classList.add('d-none');
    // in with the new
    const title = document.createElement('h3');
    title.textContent = `Psalm ${psalmDetails.number}`;
    psalmContentDiv.appendChild(title);
    // and a media link
    const songLink = document.createElement('p')
    songLink.textContent = psalmDetails.audio;
    psalmContentDiv.appendChild(songLink);
    // and more new
    const text = document.createElement('p');
    text.textContent = psalmDetails.text;
    psalmContentDiv.appendChild(text);
    // and the big reveal
    psalmDisplayDiv.classList.remove('d-none');
}
