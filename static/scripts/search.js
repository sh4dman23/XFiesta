// Assists in creating elements
function create_element(elementTag='div', elementClass=null) {
    let newElement = document.createElement(elementTag);
    if (elementClass) {
        newElement.className = elementClass;
    }
    return newElement;
}

document.addEventListener('DOMContentLoaded', function() {
    const users = document.querySelector('[name="users"]');
    const users_all = document.querySelector('[name="users_all"]');
    const users_friends= document.querySelector('[name="users_friends"]');

    const posts = document.querySelector('[name="posts"]');
    const posts_all = document.querySelector('[name="posts_all"]');
    const posts_mine = document.querySelector('[name="posts_mine"]');
    const posts_friends= document.querySelector('[name="posts_friends"]');

    const search_bar = document.getElementById('search_bar');
    const search_button = document.getElementById('search_button');
    const warning = document.getElementById('warning');

    const resultContainer = document.getElementById('resultContainer');

    const no_results = document.getElementById('no_results');

    // Search target will be initially users and option will be all
    let sTarget = "users";
    let sOption = "users_all";

    // Add results from search query with target users
    function add_user_result(result) {
        const resultDiv = create_element('div', 'search_result');
        resultDiv.style.display = 'none';

        const userDiv = create_element('div', 'user');

        const infoDiv = create_element('div', 'user-info');
        const pfpDiv = create_element('div', 'profile-pic');

        pfpDiv.innerHTML = '<img src="/static/images/user_profile_pic.png">';
        infoDiv.appendChild(pfpDiv);

        const nameDiv = create_element('div');
        nameDiv.style = 'margin-left: 0.5vw; text-align: left;';
        nameDiv.innerHTML = '<div class="name">' + result.fullname + '</div><div class="username">@' + result.username + '</div>';
        infoDiv.appendChild(nameDiv);

        const actionDiv = create_element('div', 'actions');
        const anchor = create_element('a');
        anchor.href = '/profile/' + result.username;

        const button = create_element('button', 'action-button');
        button.innerHTML = '<img src="/static/images/profile.png">';
        anchor.appendChild(button);
        actionDiv.appendChild(anchor);

        userDiv.appendChild(infoDiv);
        userDiv.appendChild(actionDiv);
        resultDiv.appendChild(userDiv);

        resultContainer.appendChild(resultDiv);
        resultDiv.style.display = 'flex';
    }

    // Add results from search query with target posts
    function add_post_result(result) {
        const resultDiv = create_element('div', 'search_result');
        resultDiv.style.display = 'none';

        const postDiv = create_element('div', 'post');

        const countDiv = create_element('div', 'counts');
        countDiv.innerHTML = '<b>Likes</b><br>' + result.likes + '<br><b>Comments</b><br>' + result.comments;
        postDiv.appendChild(countDiv);

        const imgDiv = create_element('div', 'post_image');
        if (result.imagelocation) {
            imgDiv.innerHTML = '<img src="/' + result.imagelocation + '"</img>';
        }
        postDiv.appendChild(imgDiv);

        const tagsDiv = create_element('div', 'tags');
        for (let tag of result.tags) {
            const tagDiv = create_element('div', 'tag');
            tagDiv.innerHTML = tag.tag; // tags is a list of dictionaries with only one key - 'tag'
            tagsDiv.appendChild(tagDiv);
        }
        postDiv.appendChild(tagsDiv);

        const infoDiv = create_element('div', 'post_info');
        infoDiv.innerHTML = '<div class="title"><a href="/post/' + result.id + '">' + result.title + '</a></div><p class="contents">' + result.contents + '</p>';
        postDiv.appendChild(infoDiv);

        const anchor2 = create_element('a');
        anchor2.href = '/post/' + result.id;
        anchor2.style.width = '100%';
        anchor2.appendChild(postDiv);

        resultDiv.appendChild(anchor2);
        resultContainer.appendChild(resultDiv);
        resultDiv.style.display = 'flex';
    }

    // Search targets
    document.getElementById('search_targets').addEventListener('click', function(event) {
        const target = event.target;

        // Change target to users
        if (target.name == 'users') {
            sTarget = 'users';
            users.classList.add('btn-prof');
            posts.classList.remove('btn-prof');

            // Make options visible
            document.getElementById('posts_search_options').style.display = 'none';
            document.getElementById('users_search_options').style.display = 'block';

            // Default to all
            if (sOption != 'users_all') {
                users_all.click();
            }
        }

        // Change target to posts
        if (target.name == 'posts') {
            sTarget = 'posts';
            posts.classList.add('btn-prof');
            users.classList.remove('btn-prof');

            // Make options visible
            document.getElementById('users_search_options').style.display = 'none';
            document.getElementById('posts_search_options').style.display = 'block';

            // Default to all
            if (sOption != 'posts_all') {
                posts_all.click();
            }
        }
    });

    // Search options
    document.getElementById('search_options').addEventListener('click', function(event) {
        const target = event.target;

        // All option for users target
        if (target.name == 'users_all') {
            sOption = 'users_all';
            users_all.classList.add('btn-prof');
            users_friends.classList.remove('btn-prof');
        }

        // Friends option for users target
        if (target.name == 'users_friends') {
            sOption = 'users_friends';
            users_friends.classList.add('btn-prof');
            users_all.classList.remove('btn-prof');
        }

        // All optionsfor posts target
        if (target.name == 'posts_all') {
            sOption = 'posts_all';
            posts_all.classList.add('btn-prof');
            posts_mine.classList.remove('btn-prof');
            posts_friends.classList.remove('btn-prof');
        }

        // Mine option for posts target
        if (target.name == 'posts_mine') {
            sOption = 'posts_mine';
            posts_mine.classList.add('btn-prof');
            posts_all.classList.remove('btn-prof');
            posts_friends.classList.remove('btn-prof');
        }

        // Friends option for posts target
        if (target.name == 'posts_friends') {
            sOption = 'posts_friends';
            posts_friends.classList.add('btn-prof');
            posts_mine.classList.remove('btn-prof');
            posts_all.classList.remove('btn-prof');
        }
    });

    search_bar.onkeyup = function(event) {
        if (event.key == 'Enter') {
            search_button.click();
        }
    }

    // Search
    search_button.onclick = async function() {
        if (search_bar.value.length < 1) {
            warning.innerHTML = 'Empty search query!';
            warning.style.display = 'block';
            setTimeout(function() {
                warning.style.display = 'none';
            }, 3000);

            return;
        } else if (search_bar.value.length > 640) {
            warning.innerHTML = 'Query exceeds maximum length!';
            warning.style.display = 'block';
            setTimeout(function() {
                warning.style.display = 'none';
            }, 3000);

            return;
        }

        if (!sTarget || !sOption) {
            warning.innerHTML = 'Choose search target and options!';
            warning.style.display = 'block';
            setTimeout(function() {
                warning.style.display = 'none';
            }, 3000);

            return;
        }

        try {
            const url = '/api/search';
            const data = {
                'target': sTarget,
                'option': sOption,
                'query': search_bar.value
            };

            console.log(sTarget, sOption);

            let results = document.querySelectorAll('.search_result');
            for (let result of results) {
                result.remove();
            }

            no_results.innerHTML = 'Loading...';
            no_results.style.display = 'block';

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

            no_results.style.display = 'none';

            const responseData = await response.json();
            console.log(responseData);

            if (!responseData.result) {
                throw new Error('Error processing data!');
                return;
            }
            if (!responseData.found) {
                no_results.innerHTML = 'No results were found!';
                no_results.style.display = 'block';
                return;
            }
            if (responseData.target == 'users') {
                for (let result of responseData.search_results) {
                    console.log(result);
                    add_user_result(result);
                }
            } else {
                for (let result of responseData.search_results) {
                    add_post_result(result);
                }
            }
        } catch(error) {
            console.log(error);
            warning.innerHTML = 'Error performing search!'
            warning.style.display = 'block';
            setTimeout(function() {
                warning.style.display = 'none';
            }, 3000);

            no_results.innerHTML = 'Your search results will appear here!';
            no_results.style.display = 'block';
            return;
        }
    };
});