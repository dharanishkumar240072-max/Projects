# Railway/Bus Ticket Booking Waiting-List System

A simple ticket booking system with waiting list functionality for railway and bus transportation.

## Features

- Book tickets for Railway/Bus transportation
- Automatic waiting list management
- Real-time status checking
- Seat confirmation based on availability
- Simple web interface

## Project Structure

```
├── Frontend/
│   ├── index.html    # Main HTML interface
│   ├── style.css     # Styling
│   └── script.js     # Frontend JavaScript
├── Backend/
│   ├── app.py        # Python Flask backend
│   └── requirements.txt
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to Backend folder:
   ```
   cd Backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the backend server:
   ```
   python app.py
   ```

### Frontend Setup

1. Open `Frontend/index.html` in your web browser
2. The frontend will connect to the backend at `http://localhost:5000`

## How to Use

1. **Book a Ticket**: Fill in passenger details, select transport type, route, and travel date
2. **Check Status**: Enter your ticket ID to check booking status and queue position
3. **View Waiting List**: See all current bookings and their status

## System Logic

- Maximum 5 confirmed seats per route per day
- Excess bookings go to waiting list
- Automatic promotion from waiting list when seats become available
- Unique ticket ID generation for each booking

## API Endpoints

- `POST /book` - Book a new ticket
- `GET /status/<ticket_id>` - Check ticket status
- `GET /waiting-list` - Get all tickets
- `DELETE /cancel/<ticket_id>` - Cancel a ticket
- `GET /stats` - Get system statistics