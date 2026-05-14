# Intelligent System Resource Monitoring and Prediction

## Project Overview
A real-time system monitoring dashboard that collects OS metrics, stores data in MySQL database, and provides intelligent predictions using Machine Learning.

## Features
✅ **Real-Time Metrics Dashboard** - CPU, Memory, Disk, Network usage
✅ **Running Processes Monitor** - Top 20 processes with CPU/Memory usage
✅ **Historical Logs** - Data stored in MySQL and visualized with charts
✅ **CPU Core Utilization** - Individual core monitoring
✅ **Memory Management View** - RAM and Swap memory details
✅ **System Alerts** - Automatic alerts for high resource usage
✅ **Algorithm Analysis** - Performance complexity information
✅ **ML Predictions** - Linear Regression for resource prediction

## Technologies Used
- **Backend**: Python, Flask
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **Libraries**: 
  - psutil (OS metrics collection)
  - Chart.js (Data visualization)
  - scikit-learn (Machine Learning)
  - numpy (Numerical computing)
  - mysql-connector-python (Database connection)

## Setup Instructions

### 1. Install MySQL
- Download and install MySQL Server
- Create a user with username: `root` and password: `root`
- Or update the password in `backend.py` (line 13)

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
**Option 1: Using batch file**
```bash
start.bat
```

**Option 2: Using Python**
```bash
python backend.py
```

### 4. Access Dashboard
Open your browser and go to:
```
http://localhost:5000
```

## How It Works

### Data Collection (O(1))
- Uses `psutil` library to collect real-time OS metrics
- Collects CPU, Memory, Disk, Network, and Process data
- Runs in background thread every 30 seconds

### Data Storage (O(1))
- Stores metrics in MySQL database
- Two tables: `metrics` and `alerts`
- Automatic database and table creation

### Data Retrieval (O(log n))
- Indexed queries for fast historical data retrieval
- Fetches last 24 hours of data

### Alert Detection (O(1))
- Threshold-based alert system
- CPU > 80%, Memory > 85%, Disk > 90%
- Stores alerts in database

### ML Predictions (O(n))
- Linear Regression model
- Predicts future resource usage
- Trains on historical data

## Project Structure
```
DBMS/
├── backend.py              # Flask server and monitoring logic
├── templates/
│   └── index.html         # Dashboard UI
├── requirements.txt       # Python dependencies
├── start.bat             # Quick start script
└── README.md             # This file
```

## API Endpoints
- `GET /` - Dashboard page
- `GET /api/current` - Current system metrics
- `GET /api/history` - Historical data from database
- `GET /api/processes` - Running processes
- `GET /api/cpu-cores` - CPU core utilization
- `GET /api/memory-details` - Memory details
- `GET /api/alerts` - System alerts

## Features Explained

### Real-Time Metrics Dashboard
Shows current CPU, Memory, Disk usage with progress bars and live updates every 5 seconds.

### Running Processes Monitor
Displays top 20 processes sorted by CPU usage, showing PID, name, CPU%, Memory%, and status.

### Historical Logs
Two charts:
1. Real-time chart - Last 15 data points
2. Historical chart - Last 20 data points from MySQL database

### CPU Core Utilization
Shows individual CPU core usage with progress bars for each core.

### Memory Management View
Displays:
- Physical RAM usage (used/total)
- Swap memory usage
- Total, Available, Used memory in GB

## Troubleshooting

### MySQL Connection Error
- Make sure MySQL server is running
- Check username and password in `backend.py`
- Verify MySQL service is started

### Port Already in Use
- Change port in `backend.py` (line 365): `app.run(port=5001)`

### Module Not Found
- Run: `pip install -r requirements.txt`

## Author
System Resource Monitoring Project

## License
Educational Project
