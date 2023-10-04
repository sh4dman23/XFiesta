document.addEventListener('DOMContentLoaded', function() {
    let share = document.getElementById('share_account');
    let status1 = document.getElementById('status1');
    let status2 = document.getElementById('status2');
    friend.onclick = async function() {
        if ([0, 1, 2].includes(friend_status)) {
            var aj = new XMLHttpRequest();
            aj.onreadystatechange = function() {
                if (aj.readyState == 4 && aj.status == 200) {
                    var data = JSON.parse(aj.responseText);
                    if (data.result == "Request Sent") {
                        friend_status = 2;
                        refresh_status();
                        status1.innerHTML = "Friend Request Sent!";
                    } else if (data.result == "Removed Friend") {
                        var temp = friend_status;
                        friend_status = 0;
                        refresh_status();
                        if (temp == 1) {
                            document.getElementById('friends').innerHTML = parseInt(document.getElementById('friends').innerHTML) - 1;
                            status1.innerHTML = "Friend Removed!";
                        } else if(temp == 2) {
                            status1.innerHTML = "Friend Request Canceled!";
                        }

                    }
                    setTimeout(function() {
                        status1.innerHTML = "";
                    }, 3000);
                }
            }
            aj.open("POST", "/api/manage_friends", true);
            aj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            aj.send("user_id=" + user_id);

        } else {
            var aj = new XMLHttpRequest();
            aj.onreadystatechange = function() {
                if (aj.readyState == 4 && aj.status == 200) {
                    var data = JSON.parse(aj.responseText);
                    if (data.result) {
                        friend_status = 1;
                        refresh_status();
                        document.getElementById('friends').innerHTML = parseInt(document.getElementById('friends').innerHTML) + 1;
                        status1.innerHTML = "Friend Request Accepted!";
                    } else {
                        friend_status = 3;
                        refresh_status();
                        status1.innerHTML = "Your request could not be handled! Please refresh the page";
                    }
                    setTimeout(function() {
                        status1.innerHTML = "";
                    }, 3000);
                }
            };
            aj.open("POST", "/api/accept_friend_request", true);
            aj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            aj.send("user_id=" + user_id);
        }
        refresh_status()
    }

    share.onclick = function(event) {
        event.preventDefault();
        navigator.clipboard.writeText(window.location.href).then(function() {
            status2.style.color = "green";
            status2.innerHTML = "Account link copied to clipboard!";
        }, function(err) {
            status2.style.color = "red";
            status2.innerHTML = "Could not copy link to clipboard!";
        });
        setTimeout(function() {
            status2.innerHTML = "";
        }, 1500);
    }
});