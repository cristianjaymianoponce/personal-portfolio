document.querySelectorAll('.edit-btn').forEach(button => {
    button.addEventListener('click', () => {
        let index = button.getAttribute('data-id');
        let title = document.querySelectorAll('.entry h3')[index].innerText;
        let content = document.querySelectorAll('.entry p')[index].innerText;

        document.getElementById('title').value = title;
        document.getElementById('content').value = content;
        document.getElementById('entryId').value = index;

        document.getElementById('addEntryBtn').style.display = 'none'; // Hide the Add Entry button
        document.getElementById('updateEntryBtn').style.display = 'inline-block'; // Show the Update Entry button

        // Set the form method to POST
        document.getElementById('entryForm').setAttribute('method', 'POST');
        // Set the _method input to POST
        document.querySelector('input[name="_method"]').setAttribute('value', 'POST');
    });
});

document.querySelectorAll('.delete-btn').forEach(button => {
    button.addEventListener('click', () => {
        let index = button.closest('.entry').querySelector('.edit-btn').getAttribute('data-id');
        let title = document.querySelectorAll('.entry h3')[index].innerText;

        fetch(`/delete_entry_route/${encodeURIComponent(title)}`, {
                method: 'POST'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
                location.reload();
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});

document.getElementById('updateEntryBtn').addEventListener('click', () => {
    let index = document.getElementById('entryId').value;
    let title = document.querySelectorAll('.entry h3')[index].innerText;
    let newTitle = document.getElementById('title').value;
    let newContent = document.getElementById('content').value;

    fetch(`/edit_entry/${encodeURIComponent(title)}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: newTitle,
                content: newContent
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            location.reload(); // Reload the page after successful update
        })
        .catch(error => {
            console.error('Error:', error);
        });
});