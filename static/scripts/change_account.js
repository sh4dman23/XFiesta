document.addEventListener("DOMContentLoaded", function() {
    let bool1 = true, bool2 = false, bool3 = false;

    const submit_button = document.getElementById('submit_button');

    // Check if username is availabe
    document.getElementById('username').onchange = async function() {
        var username = document.getElementById('username').value;
        var aj = new XMLHttpRequest();
        aj.onreadystatechange = function() {
            if (aj.readyState == 4 && aj.status == 200) {
                var data = JSON.parse(aj.responseText);

                if ((username != old_username && data.result) || (username == old_username)) {
                    document.getElementById('warning').style.display = "none";
                    document.getElementById('warning').innerHTML = "";
                    bool1 = true;
                    if (bool1 && bool2 && bool3) {
                        submit_button.disabled = false;
                    }
                } else {
                    document.getElementById('warning').style.display = "block";
                    document.getElementById('warning').innerHTML = "Username already exists!";
                    submit_button.disabled = true;
                    bool1 = false;
                }
            }
        }
        aj.open("POST", "/api/check_username", true);
        aj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        aj.send("username=" + username);
    }

    // Check if new password has at least 8 letters
    document.getElementById('password_new').oninput = function() {
        var password1 = document.getElementById('password_new').value;
        var password2 = document.getElementById('password_new2').value;
        if (password1.length < 8) {
            document.getElementById('warning2').style.display = "block";
            document.getElementById('warning2').innerHTML = "Password must be at least 8 characters long!";
            submit_button.disabled = true;
            bool2 = false;
        } else {
            document.getElementById('warning2').style.display = "none";
            document.getElementById('warning2').innerHTML = "";
            bool2 = true;
        }
        if (password1 != password2 && password2.length != 0) {
            document.getElementById('warning3').style.display = "block";
            document.getElementById('warning3').innerHTML = "Passwords do not match.";
            submit_button.disabled = true;
            bool3 = false;
        } else {
            document.getElementById('warning3').style.display = "none";
            document.getElementById('warning3').innerHTML = "";
            bool3 = true;
        }

        if ((bool1 && bool2 && bool3) || (password1 == '' && password2 == '')) {
            document.getElementById('warning2').style.display = "none";
            document.getElementById('warning3').style.display = "none";
            submit_button.disabled = false;
        }
    }

    // Check if the 2nd password is equal to the 1st or not
    document.getElementById('password_new2').oninput = function() {
        var password1 = document.getElementById('password_new').value;
        var password2 = document.getElementById('password_new2').value;
        if (password1 != password2) {
            document.getElementById('warning3').style.display = "block";
            document.getElementById('warning3').innerHTML = "Passwords do not match.";
            submit_button.disabled = true;
            bool3 = false;

        } else {
            document.getElementById('warning3').style.display = "none";
            document.getElementById('warning3').innerHTML = "";
            bool3 = true;
        }

        if ((bool1 && bool2 && bool3) || (password1 == '' && password2 == '')) {
            document.getElementById('warning2').style.display = "none";
            document.getElementById('warning3').style.display = "none";
            submit_button.disabled = false;
        }
    }

    // Final check for both passwords
    document.querySelector('form').addEventListener('submit', async function(event) {
        event.preventDefault();
        submit_button.disabled = true;
        submit_button.classList.add('btn-submit--loading');

        const warning = document.getElementById('warning3');

        const password_old = document.getElementById('password_old').value;
        const password_new = document.getElementById('password_new').value;

        // First check if password matches, then check if the new password meets the criteria
        try {
            const url = '/api/check_password';

            const data1 = {"password": password_old};
            const data2 = {"password": password_new};

            const [response1, response2] = await Promise.all([
                fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: JSON.stringify(data1)
                }), fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: JSON.stringify(data2)
                })
            ]);

            if (!response1.ok || (password_new && !response2.ok)) {
                throw new Error("Error sending data!");
            }

            const [responseData1, responseData2] = await Promise.all([response1.json(), response2.json()]);

            if (!responseData1.result || (password_new && !responseData2.result)) {
                throw new Error("Error processing data!");
            }

            if (!responseData1.check1) {
                warning.innerHTML = 'Incorrect Password!';
                warning.style.display = 'block';
                console.log(responseData1, responseData2);
                setTimeout(function() {
                    warning.innerHTML = '';
                    warning.style.display = 'none';
                }, 2000);
                submit_button.classList.remove('btn-submit--loading');
                submit_button.disabled = false;
                return;
            }
            if (password_new && !responseData2.check2) {
                warning.innerHTML = 'Password must contain at least 1 lowercase alphabet,<br> 1 uppercase alphabet, 1 digit and 1 special character!';
                warning.style.display = 'block';
                setTimeout(function() {
                    warning.innerHTML = '';
                    warning.style.display = 'none';
                }, 2000);
                submit_button.classList.remove('btn-submit--loading');
                submit_button.disabled = false;
                return;
            }
        } catch(error) {
            console.log(error);
            warning.innerHTML = 'Submission Failed!';
            warning.style.display = 'block';
            setTimeout(function() {
                warning.innerHTML = '';
                warning.style.display = 'none';
            }, 2000);
            submit_button.classList.remove('btn-submit--loading');
            submit_button.disabled = false;
            return;
        }

        document.querySelector('form').submit();
    });
});