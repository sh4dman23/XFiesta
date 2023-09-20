document.addEventListener("DOMContentLoaded", function() {
    let bool1 = false,
        bool2 = false,
        bool3 = false;
    document.getElementById('username').onchange = async function() {
        var username = document.getElementById('username').value;
        var aj = new XMLHttpRequest();
        aj.onreadystatechange = function() {
            if (aj.readyState == 4 && aj.status == 200) {
                var data = JSON.parse(aj.responseText);
                if (data.result) {
                    document.getElementById('warning').style.display = "none";
                    document.getElementById('warning').innerHTML = "";
                    bool1 = true;
                    if (bool1 && bool2 && bool3) {
                        document.getElementById('submit').disabled = false;
                    }
                } else {
                    document.getElementById('warning').style.display = "block";
                    document.getElementById('warning').innerHTML = "Username already exists!";
                    document.getElementById('submit').disabled = true;
                    bool1 = false;
                }
            }
        }
        aj.open("GET", "/check_username?username=" + username, true);
        aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        aj.send();
    }
    document.getElementById('password').oninput = function() {
        var password1 = document.getElementById('password').value;
        var password2 = document.getElementById('confirm').value;
        if (password1.length < 8) {
            document.getElementById('warning2').style.display = "block";
            document.getElementById('warning2').innerHTML = "Password must be at least 8 characters long!";
            document.getElementById('submit').disabled = true;
            bool2 = false;
        } else {
            document.getElementById('warning2').style.display = "none";
            document.getElementById('warning2').innerHTML = "";
            bool2 = true;
        }
        if (password1 != password2) {
            document.getElementById('warning3').style.display = "block";
            document.getElementById('warning3').innerHTML = "Passwords do not match.";
            document.getElementById('submit').disabled = true;
            bool3 = false;
        } else {
            document.getElementById('warning3').style.display = "none";
            document.getElementById('warning3').innerHTML = "";
            bool3 = true;
        }
        if (bool1 && bool2 && bool3) {
            document.getElementById('submit').disabled = false;
        }
    }
    document.getElementById('confirm').oninput = function() {
        var password1 = document.getElementById('password').value;
        var password2 = document.getElementById('confirm').value;
        if (password1 != password2) {
            document.getElementById('warning3').style.display = "block";
            document.getElementById('warning3').innerHTML = "Passwords do not match.";
            document.getElementById('submit').disabled = true;
            bool3 = false;

        } else {
            document.getElementById('warning3').style.display = "none";
            document.getElementById('warning3').innerHTML = "";
            bool3 = true;
            if (bool1 && bool2 && bool3) {
                document.getElementById('submit').disabled = false;
            }
        }
    }
});