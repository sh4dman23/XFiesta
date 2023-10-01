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
    }

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
    }

    // Add notifications
    function add_notification(notification, latest_notif) {
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
        try {
            const url = '/api/update_notifications';

            // The second child is the most recent notification (the first child is the 'mark all as read' button)
            const latest_notif = document.querySelector('.dropdown-menu :nth-child(2)');
            const data = {'id': latest_notif.getAttribute('notif_id')};

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

            for (const notification of responseData.notifications) {
                add_notification(notification, latest_notif);
            }
        } catch(error) {
            console.log(error);
        }
    }, 5000);
});