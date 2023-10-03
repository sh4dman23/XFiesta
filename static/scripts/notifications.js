document.addEventListener('DOMContentLoaded', function() {
    // Keeps track of whether or not a request for updating notifications has been sent to the server
    let is_checking_for_notifications = false;

    // Notification counter
    const notification_count = document.getElementById("unread_notification_count");

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
            document.getElementById(notification_id).classList.remove('notification-unread');
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
            const notifications = document.querySelectorAll('.notification-unread');
            for (const notification of notifications) {
                notification.classList.remove('notification-unread');
            }
        } catch(error) {
            console.log(error);
        }
    };


});