document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.dropdown-menu').addEventListener('click', function(event) {
        event.stopPropagation();
    });

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
                throw new Error('Error recieving data!');
            }

            // Decrease unread notification count
            document.getElementById("notification_count").innerHTML = parseInt(document.getElementById("notification_count").innerHTML) - 1;

            // Remove highlight
            document.querySelector('.dropdown-menu').querySelector('[notif_id="' + notification_id + '"]').classList.remove('notif-unread');
        } catch(error) {
            console.log(error);
        }
    }

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
                throw new Error('Error recieving data!');
            }

            // Set notification count to 0
            document.getElementById("notification_count").innerHTML = 0;

            // Remove highlights
            unread_notifs = document.querySelector('.dropdown-menu').querySelectorAll('.notif-unread');
            for (const notif of unread_notifs) {
                notif.classList.remove('notif-unread');
            }
        } catch(error) {
            console.log(error);
        }
    }
});