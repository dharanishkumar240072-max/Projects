document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('timesheetForm');
    const tableBody = document.getElementById('timesheetBody');

    // Load existing timesheets on page load
    loadTimesheets();

    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        addTimesheet();
    });

    function addTimesheet() {
        const formData = new FormData(form);
        const data = new URLSearchParams(formData);

        fetch('/api/timesheets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: data
        })
        .then(response => response.json())
        .then(data => {
            form.reset();
            loadTimesheets();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error adding timesheet entry');
        });
    }

    function loadTimesheets() {
        fetch('/api/timesheets')
        .then(response => response.json())
        .then(data => {
            displayTimesheets(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function displayTimesheets(timesheets) {
        tableBody.innerHTML = '';
        
        timesheets.forEach(entry => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${entry.employee}</td>
                <td>${entry.date}</td>
                <td>${entry.startTime}</td>
                <td>${entry.endTime}</td>
                <td>${entry.hours.toFixed(2)}</td>
                <td>${entry.description}</td>
                <td>
                    <button class="delete-btn" onclick="deleteTimesheet('${entry.id}')">
                        Delete
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    }

    // Make deleteTimesheet globally available
    window.deleteTimesheet = function(id) {
        if (confirm('Are you sure you want to delete this entry?')) {
            fetch(`/api/timesheets?id=${id}`, {
                method: 'DELETE'
            })
            .then(response => {
                if (response.ok) {
                    loadTimesheets();
                } else {
                    alert('Error deleting entry');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error deleting entry');
            });
        }
    };
});