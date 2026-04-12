from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from datetime import datetime
import uuid
import os

app = Flask(__name__, static_folder='../Frontend', static_url_path='')
CORS(app)

# In-memory storage for tickets
tickets = {}
waiting_queue = []
confirmed_tickets = []
MAX_CONFIRMED_SEATS = 5  # Maximum confirmed seats per route per day

class Ticket:
    def __init__(self, passenger_name, transport_type, route, travel_date):
        self.ticket_id = str(uuid.uuid4())[:8].upper()
        self.passenger_name = passenger_name
        self.transport_type = transport_type
        self.route = route
        self.travel_date = travel_date
        self.booking_time = datetime.now()
        self.status = "WAITING"
        
    def to_dict(self):
        return {
            'ticket_id': self.ticket_id,
            'passenger_name': self.passenger_name,
            'transport_type': self.transport_type,
            'route': self.route,
            'travel_date': self.travel_date,
            'status': self.status,
            'booking_time': self.booking_time.isoformat()
        }

def get_confirmed_count(route, date):
    return len([t for t in confirmed_tickets if t.route == route and t.travel_date == date])

def update_waiting_list():
    global waiting_queue, confirmed_tickets
    
    # Group by route and date
    route_date_groups = {}
    for ticket in waiting_queue[:]:
        key = (ticket.route, ticket.travel_date)
        if key not in route_date_groups:
            route_date_groups[key] = []
        route_date_groups[key].append(ticket)
    
    # Process each route-date group
    for (route, date), group_tickets in route_date_groups.items():
        confirmed_count = get_confirmed_count(route, date)
        available_seats = MAX_CONFIRMED_SEATS - confirmed_count
        
        # Confirm tickets if seats available
        for i, ticket in enumerate(group_tickets):
            if i < available_seats:
                ticket.status = "CONFIRMED"
                confirmed_tickets.append(ticket)
                waiting_queue.remove(ticket)

@app.route('/book', methods=['POST'])
def book_ticket():
    data = request.json
    
    # Validate required fields
    required_fields = ['passenger_name', 'transport_type', 'route', 'travel_date']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Create new ticket
    ticket = Ticket(
        data['passenger_name'],
        data['transport_type'],
        data['route'],
        data['travel_date']
    )
    
    # Check if seats available for immediate confirmation
    confirmed_count = get_confirmed_count(ticket.route, ticket.travel_date)
    
    if confirmed_count < MAX_CONFIRMED_SEATS:
        ticket.status = "CONFIRMED"
        confirmed_tickets.append(ticket)
    else:
        waiting_queue.append(ticket)
    
    # Store ticket
    tickets[ticket.ticket_id] = ticket
    
    return jsonify({
        'ticket_id': ticket.ticket_id,
        'status': ticket.status,
        'message': 'Ticket booked successfully'
    })

@app.route('/status/<ticket_id>', methods=['GET'])
def get_status(ticket_id):
    ticket = tickets.get(ticket_id.upper())
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    response = ticket.to_dict()
    
    # Add position in queue if waiting
    if ticket.status == "WAITING":
        position = None
        for i, waiting_ticket in enumerate(waiting_queue):
            if waiting_ticket.ticket_id == ticket_id.upper():
                position = i + 1
                break
        response['position'] = position
    
    return jsonify(response)

@app.route('/waiting-list', methods=['GET'])
def get_waiting_list():
    all_tickets = []
    
    # Add confirmed tickets
    for ticket in confirmed_tickets:
        ticket_dict = ticket.to_dict()
        all_tickets.append(ticket_dict)
    
    # Add waiting tickets with position
    for i, ticket in enumerate(waiting_queue):
        ticket_dict = ticket.to_dict()
        ticket_dict['position'] = i + 1
        all_tickets.append(ticket_dict)
    
    # Sort by booking time
    all_tickets.sort(key=lambda x: x['booking_time'])
    
    return jsonify({'tickets': all_tickets})

@app.route('/cancel/<ticket_id>', methods=['DELETE'])
def cancel_ticket(ticket_id):
    ticket = tickets.get(ticket_id.upper())
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Remove from appropriate list
    if ticket in confirmed_tickets:
        confirmed_tickets.remove(ticket)
    elif ticket in waiting_queue:
        waiting_queue.remove(ticket)
    
    # Remove from tickets dict
    del tickets[ticket_id.upper()]
    
    # Update waiting list to promote tickets
    update_waiting_list()
    
    return jsonify({'message': 'Ticket cancelled successfully'})

@app.route('/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'total_tickets': len(tickets),
        'confirmed_tickets': len(confirmed_tickets),
        'waiting_tickets': len(waiting_queue),
        'max_seats_per_route': MAX_CONFIRMED_SEATS
    })

@app.route('/')
def serve_frontend():
    return send_file('../Frontend/index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory('../Frontend', path)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("Starting Railway/Bus Ticket Booking System...")
    print(f"Backend API running on port: {port}")
    app.run(debug=False, host='0.0.0.0', port=port)