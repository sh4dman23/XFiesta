document.addEventListener('DOMContentLoaded', function() {

    // Assists in creating elements
    function create_element(elementTag='div', elementName=null, elementClass=null, elementValue=null, elementType=null) {
        let newElement = document.createElement(elementTag);
        if (elementName) {
            newElement.name = elementName;
        }
        if (elementClass) {
            newElement.className = elementClass;
        }
        if (elementValue) {
            newElement.value = elementValue;
        }
        if (elementType) {
            newElement.type = elementType;
        }
        return newElement;
    }

    const post_id = document.getElementById('post_box').getAttribute('post_id');


    let status = document.getElementById('post_box').getAttribute('interaction_status');
    const comment_count = comments;

    // Post Section Elements
    const like_button = document.getElementById('like_button');
    const dislike_button = document.getElementById('dislike_button');
    const share_button = document.getElementById('share_button');

    const popup = document.getElementById('delete_popup');
    const warning = document.getElementById('warning');

    // Comment Section Elements
    const comment_box = document.getElementById('new_comment_content');
    const post_button = document.getElementById('comment_post_button');
    const comment_warning = document.getElementById('comment_warning');

    if (owner) {
        const edit_button = document.getElementById('edit_button');
        const delete_button = document.getElementById('delete_button');
    }

    // Manage like button
    like_button.onclick = async function() {
        // Disable button for a short period
        like_button.disabled = true;
        dislike_button.disabled = true;

        var like_count = document.getElementById('post_box').querySelector('#like_count');
        if (!like_count || post_id != like_button.value) {
            window.location.reload();
        }

        var aj = new XMLHttpRequest();
        aj.onreadystatechange = async function() {
            if (aj.readyState == 4 && aj.status == 200) {
                var data = JSON.parse(aj.responseText);

                if (data.result) {
                    var button_image = like_button.querySelector('img');

                    // Manages active dislike button of a post when like button is clicked
                    document.getElementById('post_box').querySelector('[name="dislike_button"]').querySelector('img').src = "/static/images/dislike-uncolored.png";

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

                    // Update post interaction status
                    document.getElementById('post_box').setAttribute('interaction_status', status);

                    like_button.disabled = false;
                    dislike_button.disabled = false;
                }
            }
        };

        aj.open("POST", "/manage_likes", true);
        aj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        aj.send("post_id=" + post_id + "&action=" + "like");
    };

    // Manage dislike button
    dislike_button.onclick = async function() {
        // Disable both buttons for a short period
        like_button.disabled = true;
        dislike_button.disabled = true;

        var like_count = document.getElementById('post_box').querySelector('#like_count');

        if (!like_count || post_id != dislike_button.value) {
            window.location.reload();
        }

        var aj = new XMLHttpRequest();
        aj.onreadystatechange = async function() {
            if (aj.readyState == 4 && aj.status == 200) {
                var data = JSON.parse(aj.responseText);

                if (data.result) {
                    var button_image = dislike_button.querySelector('img');

                    // Manages active like button of a post when dislike button is clicked
                    document.getElementById('post_box').querySelector('[name="like_button"]').querySelector('img').src = "/static/images/like-uncolored.png";

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
                        } else if (status == 1) {
                            like_count.innerHTML = parseInt(like_count.innerHTML) - 2;
                        }

                        status = 2;
                    }

                    // Update post interaction status
                    document.getElementById('post_box').setAttribute('interaction_status', status);

                    like_button.disabled = false;
                    dislike_button.disabled = false;
                }
            }
        };

        aj.open("POST", "/manage_likes", true);
        aj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        aj.send("post_id=" + post_id + "&action=" + "dislike");
    };

    // Share button
    share_button.onclick = function() {
        event.preventDefault();
        navigator.clipboard.writeText(window.location.href).then(function() {
            warning.style.color = "green";
            warning.innerHTML = "Post link copied to clipboard!";
        }, function(err) {
            warning.style.color = "red";
            warning.innerHTML = "Could not copy link to clipboard!";
        });
        setTimeout(function() {
            warning.innerHTML = "";
        }, 1500);
    }

    // Manage post deletion
    if (owner) {
        delete_button.onclick = function() {
            document.getElementById('popup_title').innerHTML = document.getElementById('post_box').querySelector('.post-title').innerHTML;
            document.getElementById('popup_likes').innerHTML = document.getElementById('post_box').querySelector('#like_count').innerHTML;
            document.getElementById('popup_comments').innerHTML = comment_count;

            popup.style.display = 'block';
            document.body.style.overflow = 'hidden';

            document.getElementById('delete_yes').onclick = async function() {
                var aj = new XMLHttpRequest();

                aj.onreadystatechange = async function() {
                    if (aj.readyState == 4 && aj.status == 200) {
                        var data = JSON.parse(aj.responseText);
                        if (data.result) {
                            window.location.replace("http://127.0.0.1:5000/posts");
                        }
                    }
                };

                aj.open("POST", "/delete_post", true);
                aj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
                aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
                aj.send("post_id=" + post_id);
            };

            document.getElementById('delete_no').onclick = function() {
                popup.style.display = 'none';
                document.body.style.overflow = 'auto';
            };
        };
    }

    // Manage comment additions
    post_button.onclick = async function() {
        post_button.disabled = true;
        let comment_content = comment_box.value;

        if(comment_content.length < 1 || comment_content.length > 640) {
            comment_warning.innerHTML = 'Invalid Input!';
            comment_warning.style.display = 'block';

            setTimeout(function(){
                comment_warning.innerHTML = "";
                comment_warning.style.display = 'none';
            }, 2000);
        }

        comment_box.value = "";

        // Add comment via AJAX
        try {
            let url = '/api/add_comment';
            let data = {
                'post_id': post_id,
                'comment_contents': comment_content,
            };

            let response = await fetch(url, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                throw new Error('Error sending data!');
            }

            let responseData = await response.json();

            if (!responseData.result) {
                throw new Error('Error processing data!');
            }

            // Now add comment to site
            // Main container
            let commentDiv = create_element('div', null, 'comment');
            commentDiv.style.display = 'none';

            commentDiv.id = responseData.comment_id;
            commentDiv.status = 0;

            // Top div (user info and timestamp)
            let top_part = create_element('div', null, 'top-part');
            let user_info = create_element('div', null, 'user-info');
            user_info.style.marginLeft = '0%';

            let anchor1 = create_element('a');
            let profile_url = '/profile?username=' + responseData.username;
            anchor1.href = profile_url;
            anchor1.innerHTML = '<div class="profile-pic-comment"><img src="/static/images/user_profile_pic.png"></div>';
            user_info.appendChild(anchor1);

            let nameDiv = create_element('div', null, 'names');
            let anchor2 = create_element('a');
            anchor2.href = profile_url;
            anchor2.innerHTML = '<div class="name">' + responseData.fullname + '</div>';
            nameDiv.appendChild(anchor2);
            let anchor3 = create_element('a');
            anchor3.href = profile_url;
            anchor3.innerHTML = '<div class="username">@' + responseData.username + '</div>';
            nameDiv.appendChild(anchor3);
            user_info.appendChild(nameDiv);

            // Timestamp
            let timeDiv = create_element('div', null, 'post-timestamp ts-right');
            timeDiv.innerHTML = '<div>' + responseData.date + '</div> <div>' + responseData.time + '</div>';

            top_part.appendChild(user_info);
            top_part.appendChild(timeDiv);

            // Middle div (comment contents)
            let contentsDiv = create_element('div', null, 'comment-content');
            contentsDiv.innerHTML = '<p style="white-space: pre-line">' + responseData.comment_contents + '</p>';

            // Bottom div (buttons)
            let actionDiv = create_element('div', null, 'actions');
            actionDiv.style.marginTop = '0.5rem';

            // Left corner buttons for post likes and replies
            let left_buttonsDiv = create_element('div', null, 'btn-left');
            left_buttonsDiv.style.marginLeft = '0%';

            let like_comment_button = create_element('button', 'like_comment_button', 'comment-button', responseData.comment_id, 'button');
            like_comment_button.innerHTML = '<img src="/static/images/like.png">';
            left_buttonsDiv.appendChild(like_comment_button);

            let comment_like_count = create_element('div', null, 'comment-like-count');
            comment_like_count.innerHTML = 1;
            left_buttonsDiv.appendChild(comment_like_count);

            let dislike_comment_button = create_element('button', 'dislike_comment_button', 'comment-button', responseData.comment_id, 'button');
            dislike_comment_button.innerHTML = '<img src="/static/images/dislike-uncolored.png">';
            left_buttonsDiv.appendChild(dislike_comment_button);

            // Middle Warning
            let warning = create_element('div', 'warning', 'warning');

            // Right corner buttons for post deletion
            let right_buttonsDiv = create_element('div', null, 'btn-right');

            let delete_comment_button = create_element('button', 'delete_comment_button', 'comment-button', responseData.comment_id, 'button');
            delete_comment_button.innerHTML = '<img src="/static/images/delete.png" class="btn-small">';
            right_buttonsDiv.appendChild(delete_comment_button);

            let confirm_deletion_button = create_element('button', 'confirm_deletion', 'comment-button', null, 'button');
            confirm_deletion_button.style.display = 'none';
            confirm_deletion_button.innerHTML = '<img src="/static/images/Tick-logo.png" class="btn-small">';
            right_buttonsDiv.appendChild(confirm_deletion_button);

            let cancel_deletion_button = create_element('button', 'cancel_deletion', 'comment-button', null, 'button');
            cancel_deletion_button.style.display = 'none';
            cancel_deletion_button.innerHTML = '<img src="/static/images/cross-logo.png" class="btn-small">';
            right_buttonsDiv.appendChild(cancel_deletion_button);

            // Add elements to actionDiv
            actionDiv.appendChild(left_buttonsDiv);
            actionDiv.appendChild(warning);
            actionDiv.appendChild(right_buttonsDiv);

            // Add everything to comment container
            commentDiv.appendChild(top_part);
            commentDiv.appendChild(contentsDiv);
            commentDiv.appendChild(actionDiv);

            // Add the comment to the top
            parentDiv = document.getElementById('user_comment_area');
            parentDiv.insertBefore(commentDiv, parentDiv.firstChild);
            commentDiv.style.display = 'block';
            post_button.disabled = false;
        } catch(error) {
            warning.innerHTML = 'Error posting comment!<br>Refreshing page...';
            warning.style.display = 'block';
            setTimeout(function(){
                window.location.reload();
            }, 2000);
        }
    }

    // Manage click for all buttons in the comment section (via event delegation)
    document.body.addEventListener('click', async function(event) {
        const button = event.target;

        // Like buttons
        if (button.name == 'like_comment_button') {
            const like_comment_button = button;

            const comment_id = like_comment_button.value;
            const dislike_comment_button = document.getElementById(comment_id).querySelector('[name="dislike_comment_button"]');
            like_comment_button.disabled = true;
            dislike_comment_button.disabled = true;

            const comment_like_count = document.getElementById(comment_id).querySelector('.comment-like-count');
            try {
                const url = '/api/manage_comment_likes';
                const data = {
                    'comment_id': comment_id,
                    'action': 'like',
                };

                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': "XMLHttpRequest",
                    },
                    body: JSON.stringify(data),
                });

                if (!response.ok) {
                    throw new Error('Error sending request!');
                }
                const responseData = await response.json();

                if (!responseData.result) {
                    throw new Error('Error processing request!');
                }

                if (responseData.comment_status == 0) {
                    dislike_comment_button.querySelector('img').src = '/static/images/dislike-uncolored.png';
                    like_comment_button.querySelector('img').src = '/static/images/like-uncolored.png';
                } else {
                    dislike_comment_button.querySelector('img').src = '/static/images/dislike-uncolored.png';
                    like_comment_button.querySelector('img').src = '/static/images/like.png';
                }

                comment_like_count.innerHTML = responseData.comment_like_count;
                like_comment_button.disabled = false;
                dislike_comment_button.disabled = false;
            } catch(error) {
                const warning = document.getElementById(comment_id).querySelector('[name="warning"]');
                warning.innerHTML = "Failed Processing Request!<br>Refreshing page now...";
                warning.style.display = 'block';
                console.log(error);
                setTimeout(function() {
                    window.location.reload();
                }, 2000);
            }
        }

        // Dislike buttons
        if (button.name == "dislike_comment_button") {
            const dislike_comment_button = button;
            const comment_id = dislike_comment_button.value;
            const comment_like_count = document.getElementById(comment_id).querySelector('.comment-like-count');

            const like_comment_button = document.getElementById(comment_id).querySelector('[name="like_comment_button"]');
            dislike_comment_button.disabled = true;
            like_comment_button.disabled = true;

            try {
                const url = '/api/manage_comment_likes';
                const data = {
                    'comment_id': comment_id,
                    'action': 'dislike',
                };

                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': "XMLHttpRequest",
                    },
                    body: JSON.stringify(data),
                });

                if (!response.ok) {
                    throw new Error('Error sending request!');
                }
                const responseData = await response.json();

                if (!responseData.result) {
                    throw new Error('Error processing request!');
                }

                if (responseData.comment_status == 0) {
                    like_comment_button.querySelector('img').src = '/static/images/like-uncolored.png';
                    dislike_comment_button.querySelector('img').src = '/static/images/dislike-uncolored.png';
                } else {
                    like_comment_button.querySelector('img').src = '/static/images/like-uncolored.png';
                    dislike_comment_button.querySelector('img').src = '/static/images/dislike.png';
                }

                comment_like_count.innerHTML = responseData.comment_like_count;

                like_comment_button.disabled = false;
                dislike_comment_button.disabled = false;
            } catch(error) {
                let warning = document.getElementById(comment_id).querySelector('[name="warning"]');
                warning.innerHTML = "Failed Processing Request!<br>Refreshing page now...";
                warning.style.display = 'block';
                console.log(error);
                setTimeout(function() {
                    window.location.reload();
                }, 2000);
            }
        }

        // Manage comment deletion
        if (button.name == 'delete_comment_button') {
            const delete_comment_button = button;
            const comment_id = delete_comment_button.value;
            const confirm_button = document.getElementById(comment_id).querySelector('button[name="confirm_deletion"]');
            const cancel_button = document.getElementById(comment_id).querySelector('button[name="cancel_deletion"]');

            delete_comment_button.style.display = 'none';
            confirm_button.style.display = 'flex';
            cancel_button.style.display = 'flex';

            confirm_button.onclick = async function() {
                try {
                    const url = '/api/delete_comment';

                    const data = {
                        "comment_id": comment_id,
                    };

                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': "XMLHttpRequest",
                        },
                        body: JSON.stringify(data),
                    });

                    if (!response.ok) {
                        throw new Error('Error getting data!');
                    }

                    const responseData = await response.json();

                    if (!responseData.result) {
                        throw new Error('Error changing database!');
                    }

                    document.getElementById(comment_id).remove();
                } catch(error) {
                    const warning = document.getElementById(comment_id).querySelector('[name="warning"]');
                    warning.innerHTML = "Failed deleting comment!<br>Refreshing page now...";
                    warning.style.display = 'block';
                    setTimeout(function() {
                        window.location.reload();
                    }, 2000);
                }
            };

            cancel_button.onclick = function() {
                delete_comment_button.style.display = 'flex';
                confirm_button.style.display = 'none';
                cancel_button.style.display = 'none';
            };
        }
    });
});