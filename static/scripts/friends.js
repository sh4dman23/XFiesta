document.addEventListener('DOMContentLoaded', function() {
    // All Friends Tab
    document.getElementById('all_button').onclick = function() {
        document.getElementById('all_tab').style.display = 'block';
        document.getElementById('req_tab').style.display = 'none';
        document.getElementById('recom_tab').style.display = 'none';
    };

    // Friend Requests Tab
    document.getElementById('req_button').onclick = function() {
        document.getElementById('req_tab').style.display = 'block';
        document.getElementById('all_tab').style.display = 'none';
        document.getElementById('recom_tab').style.display = 'none';
    };

    // Recommendations Tab
    document.getElementById('recom_button').onclick = function() {
        document.getElementById('recom_tab').style.display = 'block';
        document.getElementById('all_tab').style.display = 'none';
        document.getElementById('req_tab').style.display = 'none';
    };

    // Remove Friends (All Tab)
    remove_buttons = document.getElementsByName('remove_button');
    for (let button of remove_buttons) {
        button.onclick = async function() {
            var friend_id = this.value;

            var aj = new XMLHttpRequest();
            aj.onreadystatechange = async function() {
                if (aj.readyState == 4 && aj.status == 200) {
                    var data = JSON.parse(aj.responseText);
                    if (data.result == "Removed Friend") {
                        document.getElementById(friend_id).remove();
                    }
                }
            };

            aj.open("POST", "/manage_friends", true)
            aj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            aj.send("user_id="+friend_id);
        };
    }

    // Accept Requests (Requests Tab)
    accept_buttons = document.getElementsByName('accept_button');
    for (var accept_button of accept_buttons) {
        accept_button.onclick = async function () {
            var user_id = this.value;
            var aj = new XMLHttpRequest();

            aj.onreadystatechange = async function() {
                if (aj.readyState == 4 && aj.status == 200) {
                    var data = JSON.parse(aj.responseText);
                    if (data.result) {
                        document.getElementById(user_id).remove();
                    }
                }
            };

            aj.open("POST", "/accept_friend_request", true);
            aj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            aj.send("user_id="+user_id);
        };
    }

    // Decline Requests (Request Tab)
    reject_buttons = document.getElementsByName('reject_button');
    for (var reject_button of reject_buttons) {
        reject_button.onclick = async function () {
            var user_id = this.value;
            var aj = new XMLHttpRequest();

            aj.onreadystatechange = async function() {
                if (aj.readyState == 4 && aj.status == 200) {
                    var data = JSON.parse(aj.responseText);
                    if (data.result) {
                        document.getElementById(user_id).remove();
                    }
                }
            };

            aj.open("POST", "/manage_friends", true);
            aj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            aj.send("user_id="+user_id);
        };
    }

    // Add Recommended Friend (Recommendations Tab)
    add_recom_buttons = document.getElementsByName('add_recommendation_button');
    for (var add_recom_button of add_recom_buttons) {
        add_recom_button.onclick = async function() {
            var user_id = this.value;
            var aj = new XMLHttpRequest();

            aj.onreadystatechange = async function() {
                if (aj.readyState == 4 && aj.status == 200) {
                    document.getElementById(user_id).remove();
                }
            };

            aj.open("POST", "/manage_friends", true);
            aj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            aj.send("user_id="+user_id);
        }
    }

    // Remove Recommendation (Recommendations Tab)
    remove_recom_buttons = document.getElementsByName('remove_recommendation_button');
    for (var remove_recom_button of remove_recom_buttons) {
        remove_recom_button.onclick = function () {
            var user_id = this.value;
            document.getElementById(user_id).remove();
        };
    }
});