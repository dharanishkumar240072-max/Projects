const API_BASE = '';

document.getElementById('bookingForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        passenger_name: document.getElementById('passengerName').value,
        transport_type: document.getElementById('transportType').value,
        route: document.getElementById('route').value,
        travel_date: document.getElementById('travelDate').value
    };

    try {
        const response = await fetch(`${API_BASE}/book`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();
        
        if (response.ok) {
            alert(`Ticket booked successfully!\nTicket ID: ${result.ticket_id}\nStatus: ${result.status}`);
            document.getElementById('bookingForm').reset();
            loadWaitingList();
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        alert('Error connecting to server. Make sure the backend is running.');
    }
});

async function checkStatus() {
    const ticketId = document.getElementById('ticketId').value;
    
    if (!ticketId) {
        alert('Please enter a ticket ID');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/status/${ticketId}`);
        const result = await response.json();
        
        const statusDiv = document.getElementById('statusResult');
        
        if (response.ok) {
            statusDiv.innerHTML = `
                <h3>Ticket Status</h3>
                <p><strong>Ticket ID:</strong> ${result.ticket_id}</p>
                <p><strong>Passenger:</strong> ${result.passenger_name}</p>
                <p><strong>Transport:</strong> ${result.transport_type}</p>
                <p><strong>Route:</strong> ${result.route}</p>
                <p><strong>Date:</strong> ${result.travel_date}</p>
                <p><strong>Status:</strong> <span class="${result.status.toLowerCase()}">${result.status}</span></p>
                ${result.position ? `<p><strong>Position in Queue:</strong> ${result.position}</p>` : ''}
            `;
        } else {
            statusDiv.innerHTML = `<p style="color: red;">Error: ${result.error}</p>`;
        }
    } catch (error) {
        document.getElementById('statusResult').innerHTML = '<p style="color: red;">Error connecting to server</p>';
    }
}

async function loadWaitingList() {
    try {
        const response = await fetch(`${API_BASE}/waiting-list`);
        const result = await response.json();
        
        const container = document.getElementById('waitingListContainer');
        
        if (response.ok && result.tickets.length > 0) {
            container.innerHTML = result.tickets.map(ticket => `
                <div class="ticket-item ${ticket.status.toLowerCase()}">
                    <strong>${ticket.ticket_id}</strong> - ${ticket.passenger_name} 
                    (${ticket.transport_type}: ${ticket.route}) - 
                    <span class="${ticket.status.toLowerCase()}">${ticket.status}</span>
                    ${ticket.position ? ` - Position: ${ticket.position}` : ''}
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p>No tickets in the system</p>';
        }
    } catch (error) {
        document.getElementById('waitingListContainer').innerHTML = '<p style="color: red;">Error loading waiting list</p>';
    }
}

// Load waiting list on page load
window.addEventListener('load', loadWaitingList);