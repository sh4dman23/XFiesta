document.addEventListener('DOMContentLoaded', function() {
    // Tab Management
    const my_posts = document.getElementById('my_posts');
    const friend_posts = document.getElementById('friend_posts');
    const popup = document.getElementById('delete_popup');
    document.getElementById('my_button').onclick = function() {
        my_posts.style.display = 'block';
        friend_posts.style.display = 'none';
    };
    document.getElementById('friends_button').onclick = function() {
        friend_posts.style.display = 'block';
        my_posts.style.display = 'none';
        popup.style.display = 'none';
    };

    const like_buttons = document.getElementsByName('like_button');
    const dislike_buttons = document.getElementsByName('dislike_button');

    const share_buttons = document.getElementsByName('share_button');

    const delete_buttons = document.getElementsByName('delete_button');

    // Like post
    for (let like_button of like_buttons) {
        like_button.onclick = async function() {
            // Disable button for a short period
            like_button.disabled = true;

            var post_id = like_button.value;
            var status = document.getElementById(post_id).getAttribute('data-value');

            var like_count = document.getElementById(post_id).querySelector('.like_count');
            if (!like_count) {
                window.location.reload();
            }

            var aj = new XMLHttpRequest();
            aj.onreadystatechange = async function() {
                if (aj.readyState == 4 && aj.status == 200) {
                    var data = JSON.parse(aj.responseText);

                    if (data.result) {
                        var button_image = like_button.querySelector('img');

                        // Manages active dislike button of a post when like button is clicked
                        document.getElementById(post_id).querySelector('[name="dislike_button"]').querySelector('img').src = "/static/images/dislike-uncolored.png";

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
                        document.getElementById(post_id).setAttribute('data-value', status);


                        like_button.disabled = false;
                    }
                }
            };

            aj.open("POST", "/api/manage_likes", true);
            aj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            aj.send("post_id=" + post_id + "&action=" + "like");
        };
    }

    // Dislike post
    for (let dislike_button of dislike_buttons) {
        dislike_button.onclick = async function() {
            // Disable button for a short period
            dislike_button.disabled = true;

            var post_id = dislike_button.value;
            var status = document.getElementById(post_id).getAttribute('data-value');

            var like_count = document.getElementById(post_id).querySelector('.like_count');
            if (!like_count) {
                window.location.reload();
            }

            var aj = new XMLHttpRequest();
            aj.onreadystatechange = async function() {
                if (aj.readyState == 4 && aj.status == 200) {
                    var data = JSON.parse(aj.responseText);

                    if (data.result) {
                        var button_image = dislike_button.querySelector('img');

                        // Manages active like button of a post when dislike button is clicked
                        document.getElementById(post_id).querySelector('[name="like_button"]').querySelector('img').src = "/static/images/like-uncolored.png";

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

                        // Update post interaction status
                        document.getElementById(post_id).setAttribute('data-value', status);

                        dislike_button.disabled = false;
                    }
                }
            };

            aj.open("POST", "/api/manage_likes", true);
            aj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            aj.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            aj.send("post_id=" + post_id + "&action=" + "dislike");
        };
    }

    // Share button
    for (let share_button of share_buttons) {
        share_button.onclick = function() {
            event.preventDefault();

            var post_id = share_button.value;
            var url = "http://127.0.0.1:5000/post/" + post_id;

            warning = document.getElementById(post_id).querySelector('.warning');

            navigator.clipboard.writeText(url).then(function() {
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
    }

    // Manage post deletion
    for (let delete_button of delete_buttons) {
        delete_button.onclick = function() {
            var post_id = delete_button.value;
            document.getElementById('popup_title').innerHTML = document.getElementById(post_id).querySelector('.post-title').innerHTML;
            document.getElementById('popup_likes').innerHTML = document.getElementById(post_id).querySelector('.like_count').innerHTML;
            document.getElementById('popup_comments').innerHTML = document.getElementById(post_id).querySelector('[name = "comment_button"]').getAttribute('comment_count');

            popup.style.display = 'block';
            document.body.style.overflow = 'hidden';

            document.getElementById('delete_yes').onclick = async function() {
                var aj = new XMLHttpRequest();

                aj.onreadystatechange = async function() {
                    if (aj.readyState == 4 && aj.status == 200) {
                        var data = JSON.parse(aj.responseText);
                        if (data.result) {
                            document.getElementById(post_id).remove();
                            popup.style.display = 'none';
                            document.body.style.overflow = 'auto';
                        }
                    }
                };

                aj.open("POST", "/api/delete_post", true);
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
});