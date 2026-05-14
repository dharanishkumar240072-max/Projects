from flask import Flask, jsonify, render_template
import mysql.connector
import psutil
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
import threading
import time
import json

app = Flask(__name__)

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dharanish@2505',
    'database': 'system_monitor'
}

# ML Models
cpu_model = LinearRegression()
memory_model = LinearRegression()
disk_model = LinearRegression()

# Alert Thresholds
THRESHOLDS = {'cpu': 80, 'memory': 85, 'disk': 90}

class SystemMonitor:
    def __init__(self):
        self.setup_database()
        self.start_monitoring()
    
    def setup_database(self):
        """Setup MySQL database and tables"""
        try:
            conn = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password']
            )
            cursor = conn.cursor()
            
            cursor.execute("CREATE DATABASE IF NOT EXISTS system_monitor")
            cursor.execute("USE system_monitor")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME,
                    cpu_percent FLOAT,
                    memory_percent FLOAT,
                    disk_percent FLOAT,
                    network_sent BIGINT,
                    network_recv BIGINT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME,
                    type VARCHAR(50),
                    message TEXT,
                    severity VARCHAR(20)
                )
            """)
            
            conn.commit()
            conn.close()
            print("✅ Database setup completed")
        except Exception as e:
            print(f"❌ Database error: {e}")
    
    def get_system_metrics(self):
        """Collect OS metrics using system calls"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('C:').percent
            network = psutil.net_io_counters()
            
            return {
                'timestamp': datetime.now(),
                'cpu_percent': cpu,
                'memory_percent': memory,
                'disk_percent': disk,
                'network_sent': network.bytes_sent,
                'network_recv': network.bytes_recv
            }
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            return None
    
    def store_metrics(self, metrics):
        """Store metrics in MySQL database - O(1) insertion"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            query = """
                INSERT INTO metrics 
                (timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                metrics['timestamp'],
                metrics['cpu_percent'],
                metrics['memory_percent'],
                metrics['disk_percent'],
                metrics['network_sent'],
                metrics['network_recv']
            ))
            
            conn.commit()
            conn.close()
            print(f"✅ Stored: CPU={metrics['cpu_percent']:.1f}%, RAM={metrics['memory_percent']:.1f}%")
        except Exception as e:
            print(f"Storage error: {e}")
    
    def check_alerts(self, metrics):
        """Algorithm for alert detection - O(1) complexity"""
        alerts = []
        
        if metrics['cpu_percent'] > THRESHOLDS['cpu']:
            alerts.append({
                'type': 'CPU',
                'message': f"High CPU usage: {metrics['cpu_percent']:.1f}%",
                'severity': 'HIGH'
            })
        
        if metrics['memory_percent'] > THRESHOLDS['memory']:
            alerts.append({
                'type': 'MEMORY',
                'message': f"High memory usage: {metrics['memory_percent']:.1f}%",
                'severity': 'HIGH'
            })
        
        if metrics['disk_percent'] > THRESHOLDS['disk']:
            alerts.append({
                'type': 'DISK',
                'message': f"High disk usage: {metrics['disk_percent']:.1f}%",
                'severity': 'CRITICAL'
            })
        
        if alerts:
            self.store_alerts(alerts)
        
        return alerts
    
    def store_alerts(self, alerts):
        """Store alerts in database"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            for alert in alerts:
                query = """
                    INSERT INTO alerts (timestamp, type, message, severity)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (
                    datetime.now(),
                    alert['type'],
                    alert['message'],
                    alert['severity']
                ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Alert storage error: {e}")
    
    def get_historical_data(self, hours=24):
        """Retrieve historical data - O(log n) with indexed queries"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            query = """
                SELECT timestamp, cpu_percent, memory_percent, disk_percent
                FROM metrics
                WHERE timestamp >= %s
                ORDER BY timestamp
            """
            
            since = datetime.now() - timedelta(hours=hours)
            cursor.execute(query, (since,))
            
            data = cursor.fetchall()
            conn.close()
            
            return data
        except Exception as e:
            print(f"Data retrieval error: {e}")
            return []
    
    def train_ml_models(self):
        """Train ML models - Linear Regression O(n) complexity"""
        try:
            data = self.get_historical_data(hours=168)  # 1 week
            
            if len(data) < 10:
                return False
            
            timestamps = [row[0] for row in data]
            cpu_data = [row[1] for row in data]
            memory_data = [row[2] for row in data]
            disk_data = [row[3] for row in data]
            
            # Feature engineering - time-based features
            X = np.array([[i, ts.hour, ts.weekday()] for i, ts in enumerate(timestamps)])
            
            # Train models
            cpu_model.fit(X, cpu_data)
            memory_model.fit(X, memory_data)
            disk_model.fit(X, disk_data)
            
            return True
        except Exception as e:
            print(f"ML training error: {e}")
            return False
    
    def predict_usage(self, hours_ahead=1):
        """ML prediction using Linear Regression"""
        try:
            future_time = datetime.now() + timedelta(hours=hours_ahead)
            X_future = np.array([[0, future_time.hour, future_time.weekday()]])
            
            predictions = {
                'cpu': max(0, min(100, cpu_model.predict(X_future)[0])),
                'memory': max(0, min(100, memory_model.predict(X_future)[0])),
                'disk': max(0, min(100, disk_model.predict(X_future)[0]))
            }
            
            return predictions
        except Exception as e:
            return {'cpu': 0, 'memory': 0, 'disk': 0}
    
    def start_monitoring(self):
        """Background monitoring thread"""
        def monitor_loop():
            while True:
                metrics = self.get_system_metrics()
                if metrics:
                    self.store_metrics(metrics)
                    self.check_alerts(metrics)
                
                # Train ML models every hour
                if datetime.now().minute == 0:
                    self.train_ml_models()
                
                time.sleep(30)  # Collect every 30 seconds
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()

# Initialize system monitor
monitor = SystemMonitor()

# API Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/current')
def current_metrics():
    """Get current system metrics"""
    metrics = monitor.get_system_metrics()
    if metrics:
        metrics['timestamp'] = metrics['timestamp'].isoformat()
    return jsonify(metrics)

@app.route('/api/history')
def historical_data():
    """Get historical data"""
    data = monitor.get_historical_data(hours=24)
    formatted_data = []
    
    for row in data:
        formatted_data.append({
            'timestamp': row[0].isoformat(),
            'cpu': row[1],
            'memory': row[2],
            'disk': row[3]
        })
    
    return jsonify(formatted_data)

@app.route('/api/predictions')
def predictions():
    """Get ML predictions"""
    monitor.train_ml_models()
    pred_1h = monitor.predict_usage(1)
    pred_6h = monitor.predict_usage(6)
    pred_24h = monitor.predict_usage(24)
    
    return jsonify({
        '1_hour': pred_1h,
        '6_hours': pred_6h,
        '24_hours': pred_24h
    })

@app.route('/api/alerts')
def get_alerts():
    """Get recent alerts"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = """
            SELECT timestamp, type, message, severity
            FROM alerts
            WHERE timestamp >= %s
            ORDER BY timestamp DESC
            LIMIT 20
        """
        
        since = datetime.now() - timedelta(hours=24)
        cursor.execute(query, (since,))
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'timestamp': row[0].isoformat(),
                'type': row[1],
                'message': row[2],
                'severity': row[3]
            })
        
        conn.close()
        return jsonify(alerts)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    import webbrowser
    import threading
    
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("🚀 Starting Intelligent System Resource Monitor")
    print("📊 Database: MySQL")
    print("🤖 ML: Linear Regression")
    print("🌐 Opening: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)