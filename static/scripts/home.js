// Assists in creating elements
function create_element(elementTag='div', elementName=null, elementClass=null) {
    let newElement = document.createElement(elementTag);
    if (elementName) {
        newElement.name = elementName;
    }
    if (elementClass) {
        newElement.className = elementClass;
    }
    return newElement;
}

document.addEventListener('DOMContentLoaded', function() {
    // Keeps track of whether or not a request for updating notifications has been sent to the server
    let is_checking_for_notifications = false;

    // Notification counter
    const notification_count = document.getElementById("notification_count");

    // Do not close dropdown menu on click
    document.querySelector('.dropdown-menu').addEventListener('click', function(event) {
        event.stopPropagation();
    });

    // Mark notification as read
    window.mark_as_read = async function(notification_id) {
        try {
            const url = '/api/mark_notification_as_read';
            const data = {'id': notification_id};

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error('Error processing data!');
            }

            const responseData = await response.json();

            if (!responseData.result) {
                throw new Error('Error retrieving data!');
            }

            // Decrease unread notification count
            notification_count.innerHTML = parseInt(notification_count.innerHTML) - 1;

            // Remove highlight
            document.querySelector('.dropdown-menu').querySelector('[notif_id="' + notification_id + '"]').classList.remove('notif-unread');
        } catch(error) {
            console.log(error);
        }
    };

    // Mark all notifications as read
    window.mark_all_as_read = async function() {
        try {
            const url = '/api/mark_notification_as_read';
            const data = {'optional': 'all'};

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error('Error processing data!');
            }

            const responseData = await response.json();

            if (!responseData.result) {
                throw new Error('Error retrieving data!');
            }

            // Set notification count to 0
            notification_count.innerHTML = 0;

            // Remove highlights
            unread_notifs = document.querySelector('.dropdown-menu').querySelectorAll('.notif-unread');
            for (const notif of unread_notifs) {
                notif.classList.remove('notif-unread');
            }
        } catch(error) {
            console.log(error);
        }
    };

    // Add notifications
    function add_notification(notification) {
        // Select the latest notification every time
        const latest_notif = document.querySelector('.dropdown-menu :nth-child(2)');
        const menu = document.querySelector('.dropdown-menu');

        // Increase notification count
        notification_count.innerHTML = parseInt(notification_count.innerHTML) + 1;

        const notificationDiv = create_element('li', 'notif', 'notif notif-unread');
        notificationDiv.setAttribute('notif_id', notification.id);

        const detailsDiv = create_element('a', null, 'dropdown-item');
        detailsDiv.href = notification.href;
        detailsDiv.target = '__blank';
        detailsDiv.innerHTML = notification.details;

        const markDiv = create_element('a', null, 'mark-as-read');
        markDiv.setAttribute('onclick', "mark_as_read(" + notification.id + ")");
        markDiv.innerHTML = 'Mark as read';

        notificationDiv.appendChild(detailsDiv);
        notificationDiv.appendChild(markDiv);

        // Add notification before the second child (the latest notification before insert)
        menu.insertBefore(notificationDiv, latest_notif);
    }

    // Update notifications via AJAX
    setInterval(async function(){
        if (!is_checking_for_notifications) {
            is_checking_for_notifications = true;
            try {
                const url = '/api/update_notifications';

                // The second child is the most recent notification (the first child is the 'mark all as read' button)
                const current_latest_notif = document.querySelector('.dropdown-menu :nth-child(2)');
                const data = {'last_notif_id': (current_latest_notif != null ? current_latest_notif.getAttribute('notif_id') : 0)};

                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    throw new Error('Error processing data!');
                }

                const responseData = await response.json();

                if (!responseData.result) {
                    throw new Error('Error retrieving data!');
                } else if (!responseData.found) {
                    is_checking_for_notifications = false;
                    return;
                }

                // If there are no unread notifications,
                if (parseInt(notification_count.innerHTML) == 0) {
                    if (document.getElementById('no_notifications') != null) {
                        document.getElementById('no_notifications').remove();
                    }
                    const mark_all_as_read = create_element('li');
                    mark_all_as_read.style.marginBottom = '5px';
                    mark_all_as_read.innerHTML = '<a class="mark-as-read" style="text-align: center; width: 100% !important; margin-right: 0% !important;" onclick="mark_all_as_read();">Mark all as read</a>';
                    const menu = document.querySelector('.dropdown-menu');
                    menu.insertBefore(mark_all_as_read, menu.children[0]);
                }
                for (const notification of responseData.notifications) {
                    add_notification(notification);
                }
            } catch(error) {
                console.log(error);
            }

            is_checking_for_notifications = false;
        }
    }, 5000);

    // Buttons in post section
    document.querySelector('.post-feed').addEventListener('click', async function(event) {
        const target = event.target;

        // Likes and dislikes
        if (target.name == 'like_button' || target.name == 'dislike_button') {
            const button = target;

            const post_id = button.value;
            const post = document.querySelector('[post_id="' + post_id + '"]');

            const button_image = button.querySelector('img');
            const like_count = post.querySelector('.like_count');

            const like_button = post.querySelector('[name="like_button"]');
            const dislike_button = post.querySelector('[name="dislike_button"]');

            const warning = post.querySelector('.warning');

            like_button.disabled = true;
            dislike_button.disabled = true;

            let status = post.getAttribute('status');
            try {
                const url = '/api/manage_likes';
                const data = {
                    'post_id': post_id,
                    'action': 'like'
                };

                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded', // Content type is not json because this api was made when I used XMLHttpRequest and not Fetch
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: new URLSearchParams(data).toString()
                });

                if (!response.ok) {
                    throw new Error('Error processing data!');
                }

                const responseData = await response.json();

                if (!responseData.result) {
                    throw new Error('Error retrieving data!');
                }

                if (button.name == 'like_button') {
                    dislike_button.querySelector('img').src = '/static/images/dislike-uncolored.png';
                    if (status == 1) {
                        // Unliked
                        button_image.src = "/static/images/like-uncolored.png";
                        like_count.innerHTML = parseInt(like_count.innerHTML) - 1;
                        status = 0;
                    } else {
                        // Liked
                        button_image.src = "/static/images/like.png";

                        if (status == 0) {
                            like_count.innerHTML = parseInt(like_count.innerHTML) + 1;
                        } else {
                            like_count.innerHTML = parseInt(like_count.innerHTML) + 2;
                        }

                        status = 1;
                    }
                } else if (button.name == 'dislike_button') {
                    like_button.querySelector('img').src = '/static/images/like-uncolored.png';
                    if (status == 2) {
                        // Removed Dislike
                        button_image.src = "/static/images/dislike-uncolored.png";
                        like_count.innerHTML = parseInt(like_count.innerHTML) + 1;
                        status = 0;
                    } else {
                        // Disliked
                        button_image.src = "/static/images/dislike.png";

                        if (status == 0) {
                            like_count.innerHTML = parseInt(like_count.innerHTML) - 1;
                        } else {
                            like_count.innerHTML = parseInt(like_count.innerHTML) - 2;
                        }

                        status = 2;
                    }
                }

            } catch(error) {
                console.log(error);
                warning.innerHTML = 'Your request could not be processed.'
                warning.style.display = 'block';
                setTimeout(function() {
                    warning.style.display = 'none';
                    warning.innerHTML = '';
                }, 2000);
            }

            post.setAttribute('status', status);
            like_button.disabled = false;
            dislike_button.disabled = false;
        }

        // Share
        if (target.name == 'share_button') {
            const share_button = target;

            const post_id = share_button.value;
            const url = 'http://127.0.0.1:5000/post/' + post_id;

            warning = document.querySelector('[post_id="' + post_id + '"]').querySelector('.warning');

            navigator.clipboard.writeText(url).then(function() {
                warning.style.color = 'green';
                warning.innerHTML = 'Post link copied to clipboard!';
                warning.style.display = 'block';
            }, function(err) {
                warning.style.color = 'red';
                warning.innerHTML = 'Could not copy link to clipboard!';
                warning.style.display = 'block';
            });
            setTimeout(function() {
                warning.innerHTML = '';
                warning.style.display = 'none';
            }, 1500);
        }

        // Delete
        if (target.name == 'delete_button') {
            // Show popup
            const popup = document.getElementById('delete_popup');
            const post = document.querySelector('[post_id="' + target.value + '"]');
            popup.querySelector('#popup_title').innerHTML = post.querySelector('.post-title').innerHTML;
            popup.querySelector('#popup_likes').innerHTML = post.querySelector('.like_count').innerHTML;
            popup.querySelector('#popup_comments').innerHTML = post.querySelector('[name = "comment_button"]').getAttribute('comment_count');

            popup.style.display = 'block';
            document.body.style.overflow = 'hidden';

            popup.querySelector('#delete_yes').onclick = async function() {
                try {
                    const url = '/api/delete_post';
                    const data = {
                        'post_id': post.getAttribute('post_id')
                    };

                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: new URLSearchParams(data).toString()
                    });

                    if (!response.ok) {
                        throw new Error('Error processing data!');
                    }

                    const responseData = await response.json();

                    if (!responseData.result) {
                        throw new Error('Error retrieving data!');
                    }

                    post.remove();
                } catch(error) {
                    console.log(error);
                    const warning = post.querySelector('.warning');
                    warning.innerHTML = 'Your request could not be processed!';
                    warning.style.display = 'block';
                    setTimeout(function() {
                        warning.innerHTML = '';
                        warning.style.display = 'none';
                    }, 2000);
                }
                popup.style.display = 'none';
                document.body.style.overflow = 'auto';
            };

            popup.querySelector('#delete_no').onclick = function() {
                popup.style.display = 'none';
                document.body.style.overflow = 'auto';
            };
        }
    });
});