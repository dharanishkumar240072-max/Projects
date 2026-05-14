from flask import Flask, jsonify, render_template
import sqlite3
import psutil
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
import threading
import time
import os

app = Flask(__name__)

# Database Configuration
DB_FILE = 'system_monitor.db'

# ML Models
cpu_model = LinearRegression()
memory_model = LinearRegression()

class SystemMonitor:
    def __init__(self):
        self.setup_database()
        self.start_monitoring()
    
    def setup_database(self):
        """Setup SQLite database and tables"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    network_sent INTEGER,
                    network_recv INTEGER
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    type TEXT,
                    message TEXT,
                    severity TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            print("Database setup completed successfully.")
        except Exception as err:
            print(f"Database error: {err}")
    
    def get_system_metrics(self):
        """Collect OS metrics using psutil"""
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
            print("Error collecting metrics: " + str(e))
            return None
    
    def store_metrics(self, metrics):
        """Store metrics in SQLite database"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            query = """
                INSERT INTO metrics 
                (timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv)
                VALUES (?, ?, ?, ?, ?, ?)
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
            cpu_val = round(metrics['cpu_percent'], 1)
            mem_val = round(metrics['memory_percent'], 1)
            print("Stored: CPU=" + str(cpu_val) + "%, RAM=" + str(mem_val) + "%")
        except Exception as e:
            print("Storage error: " + str(e))
    
    def check_alerts(self, metrics):
        """Check for system alerts"""
        alerts = []
        
        cpu_val = round(metrics['cpu_percent'], 1)
        mem_val = round(metrics['memory_percent'], 1)
        disk_val = round(metrics['disk_percent'], 1)
        
        if metrics['cpu_percent'] > 80:
            alerts.append({
                'type': 'CPU',
                'message': 'High CPU usage: ' + str(cpu_val) + '%',
                'severity': 'HIGH'
            })
        
        if metrics['memory_percent'] > 85:
            alerts.append({
                'type': 'MEMORY',
                'message': 'High memory usage: ' + str(mem_val) + '%',
                'severity': 'HIGH'
            })
        
        if metrics['disk_percent'] > 90:
            alerts.append({
                'type': 'DISK',
                'message': 'High disk usage: ' + str(disk_val) + '%',
                'severity': 'CRITICAL'
            })
        
        if alerts:
            self.store_alerts(alerts)
        
        return alerts
    
    def store_alerts(self, alerts):
        """Store alerts in database"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            for alert in alerts:
                query = """
                    INSERT INTO alerts (timestamp, type, message, severity)
                    VALUES (?, ?, ?, ?)
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
            print("Alert storage error: " + str(e))
    
    def get_historical_data(self, hours=24):
        """Retrieve historical data from database"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            query = """
                SELECT timestamp, cpu_percent, memory_percent, disk_percent
                FROM metrics
                WHERE timestamp >= ?
                ORDER BY timestamp
            """
            
            since = datetime.now() - timedelta(hours=hours)
            cursor.execute(query, (since,))
            
            data = cursor.fetchall()
            conn.close()
            
            return data
        except Exception as e:
            print("Data retrieval error: " + str(e))
            return []
    
    def start_monitoring(self):
        """Background monitoring thread"""
        def monitor_loop():
            while True:
                metrics = self.get_system_metrics()
                if metrics:
                    self.store_metrics(metrics)
                    self.check_alerts(metrics)
                
                time.sleep(5)  # Collect every 5 seconds
        
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
    try:
        cpu = psutil.cpu_percent(interval=None)
        if cpu == 0.0:
            cpu = psutil.cpu_percent(interval=0.1)
        
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('C:').percent
        network = psutil.net_io_counters()
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': float(cpu),
            'memory_percent': float(memory),
            'disk_percent': float(disk),
            'network_sent': int(network.bytes_sent),
            'network_recv': int(network.bytes_recv)
        }
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/history')
def historical_data():
    """Get historical data from database"""
    data = monitor.get_historical_data(hours=24)
    formatted_data = []
    
    for row in data:
        formatted_data.append({
            'timestamp': row[0],
            'cpu': row[1],
            'memory': row[2],
            'disk': row[3]
        })
    
    return jsonify(formatted_data)

@app.route('/api/processes')
def get_processes():
    """Get running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu': pinfo['cpu_percent'] or 0,
                    'memory': pinfo['memory_percent'] or 0,
                    'status': pinfo['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        processes.sort(key=lambda x: x['cpu'], reverse=True)
        return jsonify(processes[:30])
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/cpu-cores')
def get_cpu_cores():
    """Get individual CPU core utilization"""
    try:
        core_percentages = psutil.cpu_percent(interval=0.1, percpu=True)
        cores = []
        for i, percent in enumerate(core_percentages):
            cores.append({
                'core': i,
                'usage': float(percent)
            })
        return jsonify({
            'cores': cores,
            'count': len(cores),
            'average': float(sum(core_percentages) / len(core_percentages))
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/memory-details')
def get_memory_details():
    """Get detailed memory information"""
    try:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return jsonify({
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'free': mem.free,
            'percent': mem.percent,
            'total_gb': round(mem.total / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'free_gb': round(mem.free / (1024**3), 2),
            'swap_total_gb': round(swap.total / (1024**3), 2),
            'swap_used_gb': round(swap.used / (1024**3), 2),
            'swap_percent': swap.percent
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/alerts')
def get_alerts():
    """Get recent alerts"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        query = """
            SELECT timestamp, type, message, severity
            FROM alerts
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT 20
        """
        
        since = datetime.now() - timedelta(hours=24)
        cursor.execute(query, (since,))
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'timestamp': row[0],
                'type': row[1],
                'message': row[2],
                'severity': row[3]
            })
        
        conn.close()
        return jsonify(alerts)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/database-records')
def get_database_records():
    """Get raw database records"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        query = """
            SELECT id, timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv
            FROM metrics
            ORDER BY timestamp DESC
            LIMIT 20
        """
        
        cursor.execute(query)
        
        records = []
        for row in cursor.fetchall():
            records.append({
                'id': row[0],
                'timestamp': row[1],
                'cpu': row[2],
                'memory': row[3],
                'disk': row[4],
                'network_sent': row[5],
                'network_recv': row[6]
            })
        
        conn.close()
        return jsonify(records)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("Starting Intelligent System Resource Monitor")
    print("Database: SQLite")
    print("ML: Linear Regression")
    print("Opening: http://localhost:5000")
    
    # Initialize CPU monitoring
    psutil.cpu_percent(interval=None)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
