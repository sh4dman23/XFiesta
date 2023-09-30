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

document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    const no_message = document.getElementById('no_message');
    const send_box = document.getElementById('send_box');
    const send_button = document.getElementById('send_button');
    const warning = document.getElementById('send_warning');

    // Keep track of whether or not user is sending a message
    let is_adding = false;
    let last_message_sent_id = null;

    // Check whether or not a request for new messages is already being processed
    let is_checking = false;

    // Checks if there are no messages in the chat
    function check_empty_chat() {
        no_message.style.display = (document.getElementsByClassName('message-container')).length > 0 ? 'none' : 'flex';
    }

    // Adds element to chat container
    function add_comment(data) {
        const messageDiv = create_element('div', 'message', 'message-container');
        messageDiv.style.display = 'none';
        messageDiv.id = data.message_id;

        const topDiv = create_element('div', null, 'top-part');

        const nameDiv = create_element('div', null, 'name');
        const anchor = create_element('a');
        anchor.tabindex = '-1';
        anchor.href = '/profile/' + data.username;
        anchor.innerHTML = data.username;
        nameDiv.appendChild(anchor);
        topDiv.appendChild(nameDiv);

        const timeDiv = create_element('div', null, 'name');
        timeDiv.style = 'font-weight: normal; margin-right: auto; margin-left: 10px';
        timeDiv.innerHTML = data.message_time + ' ' + data.message_date;
        topDiv.appendChild(timeDiv);

        // Add delete buttons only if the message is from the user
        if (data.owner) {
            const buttonDiv = create_element('div', null, 'actions');
            const deleteButton = create_element('button', 'delete_message_button', 'action-button btn-big', data.message_id, 'button');
            deleteButton.innerHTML = '<img alt="Delete Message" src="/static/images/delete.png">';
            buttonDiv.appendChild(deleteButton);

            const confirmButton = create_element('button', 'confirm_deletion', 'action-button', data.message_id, 'button');
            confirmButton.style.display = 'none';
            confirmButton.innerHTML = '<img alt="Confirm Deletion" src="/static/images/Tick-logo.png" style="width: 15px;">';
            buttonDiv.appendChild(confirmButton);

            const cancelButton = create_element('button', 'cancel_deletion', 'action-button', data.message_id, 'button');
            cancelButton.style.display = 'none';
            cancelButton.innerHTML = '<img alt="Cancel Deletion" src="/static/images/cross-logo.png" style="width: 15px;">';
            buttonDiv.appendChild(cancelButton);

            topDiv.appendChild(buttonDiv);
        }

        const contentsDiv = create_element('p');
        contentsDiv.innerHTML = data.contents;
        contentsDiv.style.whiteSpace = 'pre-line';

        const warningDiv = create_element('div', 'warning', 'warning');

        messageDiv.appendChild(topDiv);
        messageDiv.appendChild(contentsDiv);
        messageDiv.appendChild(warningDiv);

        chatContainer.appendChild(messageDiv);
        messageDiv.style.display = 'block';
    }

    document.body.style.display = 'block';
    chatContainer.scrollTop = chatContainer.scrollHeight;
    document.getElementById('main-container').scrollIntoView({block: 'center'});

    check_empty_chat();

    // Send message
    send_box.addEventListener('keyup', function(event) {
        if (send_box.value.length > 640) {
            warning.innerHTML = 'Maximum characters reached!';
            warning.style.display = 'block';
            send_box.value = send_box.value.slice(0, maxLength);
        } else {
            warning.style.display = 'none';
        }
        if (event.key == 'Enter' && !event.shiftKey) {
            send_box.disabled = true;
            send_button.click();
        }
    });

    send_button.onclick = async function() {
        send_box.disabled = true;
        const contents = send_box.value;
        send_button.disabled = true;
        if (contents.length == 0) {
            warning.innerHTML = 'Empty messages will not be sent!';
            warning.style.display = 'block';
            setTimeout(function() {
                warning.innerHTML = '';
                warning.style.display = 'none';
            }, 2000);
            send_box.disabled = false;
            send_button.disabled = false;
            return;
        }
        if (contents.length > 640) {
            warning.innerHTML = 'Too many characters!';
            warning.style.display = 'block';
            send_box.disabled = false;
            send_button.disabled = false;
            return;
        }

        try {
            is_adding = true;

            const url = '/api/send_message';
            const data = {
                "inbox_id": inbox_id,
                "reciever_id": user_id,
                'contents': contents
            };

            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error("Error sending request!");
            }

            const responseData = await response.json();

            if (!responseData.result) {
                throw new Error("Error processing request!");
            }

            // Add comment at the bottom
            send_box.value = "";
            add_comment(responseData);

            // Update inbox id if not found
            if (inbox_id == null) {
                inbox_id = responseData.inbox_id;
            }

            // Update last message id
            last_message_id = responseData.message_id;
            last_message_sent_id = responseData.message_id;

        } catch(error) {
            console.log(error);
            warning.innerHTML = 'Your message could not be sent!';
            warning.style.display = 'block';
            setTimeout(function() {
                warning.innerHTML = '';
                warning.style.display = 'none';
            }, 2500);
        }

        is_adding = false;
        send_box.disabled = false;
        send_button.disabled = false;
        send_box.focus();

        check_empty_chat();

        // Scroll to new message
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: 'smooth'
        });
    };

    // Periodically ask the server for new messages
    setInterval(async function() {
        const atBottom = (chatContainer.scrollTop + chatContainer.clientHeight) >= chatContainer.scrollHeight;
        if (!is_adding && !is_checking) {
            is_checking = true;
            try {
                const url = '/api/check_message';
                const data = {
                    "inbox_id": inbox_id,
                    "last_message_id": last_message_id,
                    "person_id": user_id    // Other person's id
                };
                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    throw new Error("Error sending request!");
                }

                const responseData = await response.json();

                if (!responseData.result) {
                    throw new Error("Error processing request!");
                }

                // Update inbox id, if null
                if (inbox_id == null) {
                    inbox_id = responseData.inbox_id;
                }

                if (!responseData.new) {
                    is_checking = false;
                    return;
                }

                // Update last message
                last_message_id = responseData.last_message_id;

                // Add the new comment(s)
                for (let comment_data of responseData.comment_list) {
                    if (!last_message_sent_id || comment_data.message_id != last_message_sent_id) {
                        add_comment(comment_data);
                    }
                }

                if (atBottom) {
                    chatContainer.scrollTo({
                        top: chatContainer.scrollHeight,
                        behavior: 'smooth'
                    });
                }

                check_empty_chat()
            } catch(error) {
                // Don't bother
            }

            is_checking = false;
        }
    }, 700);

    // Periodically ask the server for deleted messages
    setInterval(async function() {
        if (inbox_id) {
            try {
                const url = '/api/check_deleted';
                const data = {
                    "inbox_id": inbox_id
                };

                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    return;
                }

                const responseData = await response.json();

                if (!responseData.result) {
                    return;
                }

                // No new deleted message were found
                if (!responseData.deleted) {
                    return;
                }

                last_message_id = responseData.last_message_id;

                if (responseData.deleted_messages) {
                    for (let deleted_message of responseData.deleted_messages) {
                        const messageBox = document.getElementById(deleted_message.message_id);

                        if (messageBox) {
                            messageBox.remove();
                        }
                    }
                }

                check_empty_chat();
            } catch(error) {
                // Pass
            }
        }
    }, 1500);

    // Delete buttons
    chatContainer.addEventListener('click', async function(event) {
        const target = event.target;

        if (target.name == 'delete_message_button') {
            const delete_message_button = target;
            const message_id = delete_message_button.value;

            const confirm_button = document.getElementById(message_id).querySelector('[name="confirm_deletion"]');
            const cancel_button = document.getElementById(message_id).querySelector('[name="cancel_deletion"]');
            const warning = document.getElementById(message_id).querySelector('.warning');


            delete_message_button.style.display = 'none';
            confirm_button.style.display = 'flex';
            cancel_button.style.display = 'flex';

            confirm_button.onclick = async function() {
                try {
                    const url = '/api/delete_message';
                    const data = {
                        'message_id': message_id
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
                        throw new Error("Error processing data!");
                    }

                    const responseData = await response.json();

                    if (!responseData.result) {
                        throw new Error("Error processing data!")
                    }

                    document.getElementById(message_id).remove();

                } catch(error) {
                    console.log(error);
                    warning.innerHTML = 'Failed deleting message!';
                    warning.style.display = 'block';

                    setTimeout(function(){
                        warning.style.display = 'none';
                        warning.innerHTML = '';
                    }, 2000);
                }

                check_empty_chat();
            }

            cancel_button.onclick = function() {
                confirm_button.style.display = 'none';
                cancel_button.style.display = 'none';
                delete_message_button.style.display = 'flex';
            }
        }
    });
});