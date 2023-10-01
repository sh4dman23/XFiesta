document.addEventListener('DOMContentLoaded', function() {
    let bool1 = false, bool2 = false, bool3 = false;

    const warning = document.getElementById('warning');
    const warning2 = document.getElementById('warning2');
    const warning3 = document.getElementById('warning3');

    const submit_button = document.getElementById('submit_button');

    // Check username
    document.getElementById('username').onchange = async function() {
        var username = document.getElementById('username').value;
        var aj = new XMLHttpRequest();
        aj.onreadystatechange = function() {
            if (aj.readyState == 4 && aj.status == 200) {
                var data = JSON.parse(aj.responseText);
                if (data.result) {
                    warning.style.display = "none";
                    warning.innerHTML = "";
                    bool1 = true;
                    if (bool1 && bool2 && bool3) {
                        submit_button.disabled = false;
                    }
                } else {
                    warning.style.display = "block";
                    warning.innerHTML = "Username already exists!";
                    submit_button.disabled = true;
                    bool1 = false;
                }
            }
        }
        aj.open("POST", "/api/check_username", true);
        aj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        aj.send("username=" + username);
    };

    // Check passwords
    document.getElementById('password').oninput = function() {
        var password1 = document.getElementById('password').value;
        var password2 = document.getElementById('confirm').value;
        if (password1.length < 8) {
            warning2.style.display = "block";
            warning2.innerHTML = "Password must be at least 8 characters long!";
            submit_button.disabled = true;
            bool2 = false;
        } else {
            warning2.style.display = "none";
            warning2.innerHTML = "";
            bool2 = true;
        }
        if (password1 != password2 && password2.length != 0) {
            warning3.style.display = "block";
            warning3.innerHTML = "Passwords do not match.";
            submit_button.disabled = true;
            bool3 = false;
        } else {
            warning3.style.display = "none";
            warning3.innerHTML = "";
            bool3 = true;
        }
        if (bool1 && bool2 && bool3) {
            submit_button.disabled = false;
        }
    };
    document.getElementById('confirm').oninput = function() {
        var password1 = document.getElementById('password').value;
        var password2 = document.getElementById('confirm').value;
        if (password1 != password2) {
            warning3.style.display = "block";
            warning3.innerHTML = "Passwords do not match.";
            submit_button.disabled = true;
            bool3 = false;

        } else {
            warning3.style.display = "none";
            warning3.innerHTML = "";
            bool3 = true;
            if (bool1 && bool2 && bool3) {
                submit_button.disabled = false;
            }
        }
    };

    // Final check for password
    document.querySelector('form').addEventListener('submit', async function(event) {
        event.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const url = '/api/check_password';
            const data = {
                'username': username,
                'password': password
            };

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error('Error sending data!');
            }

            const responseData = await response.json();

            if (!responseData.result) {
                throw new Error('Error processing data');
            }

            if (!responseData.user_exists) {
                console.log(responseData);
            }

            if (!responseData.check2) {
                warning3.innerHTML = 'Password must contain at least 1 lowercase alphabet,<br> 1 uppercase alphabet, 1 digit and 1 special character!';
                warning3.style.display = 'block';
                setTimeout(function() {
                    warning3.innerHTML = '';
                    warning3.style.display = 'none';
                }, 2000);
                return;
            }

        } catch(error) {
            console.log(error);
            warning3.innerHTML = 'Submission Failed!';
            warning3.style.display = 'block';
            setTimeout(function() {
                warning3.innerHTML = '';
                warning3.style.display = 'none';
            }, 2000);
            return;
        }

        document.querySelector('form').submit();
    });
});
