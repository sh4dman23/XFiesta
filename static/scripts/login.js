document.addEventListener('DOMContentLoaded', function() {
    const warning = document.getElementById('warning');
    const submit_button = document.querySelector('.btn-submit');

    document.querySelector('form').addEventListener('submit', async function(event) {
        event.preventDefault();
        submit_button.disabled = true;
        submit_button.classList.add('btn-submit--loading');

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
                warning.innerHTML = 'Invalid username!';
                warning.style.display = 'block';
                setTimeout(function() {
                    warning.innerHTML = '';
                    warning.style.display = 'none';
                }, 2000);
                submit_button.classList.remove('btn-submit--loading');
                submit_button.disabled = false;
                return;
            }

            if (!responseData.check1) {
                warning.innerHTML = 'Incorrect password!';
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

        // Send user's timezone offset
        const tz_offset = document.createElement('input');
        tz_offset.hidden = true;
        tz_offset.name = 'user_timezone_offset';
        tz_offset.value = new Date().getTimezoneOffset();
        document.querySelector('form').appendChild(tz_offset);
        document.querySelector('form').submit();
    });
});