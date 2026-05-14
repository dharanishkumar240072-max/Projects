from flask import Flask, jsonify, render_template
import mysql.connector
import threading
import time
from datetime import datetime
import subprocess
import json
import os

app = Flask(__name__)

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dharanish@2505',
    'database': 'system_monitor'
}

# Global variable to store current metrics
current_metrics = {
    'cpu_percent': 0,
    'memory_percent': 0,
    'disk_percent': 0,
    'timestamp': datetime.now()
}

def get_cpu_usage():
    """Get CPU usage using Windows command"""
    try:
        result = subprocess.run(['wmic', 'cpu', 'get', 'loadpercentage', '/value'], 
                              capture_output=True, text=True, shell=True)
        for line in result.stdout.split('\n'):
            if 'LoadPercentage' in line:
                return float(line.split('=')[1])
    except:
        pass
    return 0

def get_memory_usage():
    """Get memory usage using Windows command"""
    try:
        # Get total memory
        result = subprocess.run(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory', '/value'], 
                              capture_output=True, text=True, shell=True)
        total_memory = 0
        for line in result.stdout.split('\n'):
            if 'TotalPhysicalMemory' in line:
                total_memory = int(line.split('=')[1])
                break
        
        # Get available memory
        result = subprocess.run(['wmic', 'OS', 'get', 'FreePhysicalMemory', '/value'], 
                              capture_output=True, text=True, shell=True)
        free_memory = 0
        for line in result.stdout.split('\n'):
            if 'FreePhysicalMemory' in line:
                free_memory = int(line.split('=')[1]) * 1024  # Convert KB to bytes
                break
        
        if total_memory > 0:
            used_memory = total_memory - free_memory
            return (used_memory / total_memory) * 100
    except:
        pass
    return 0

def get_disk_usage():
    """Get disk usage using Windows command"""
    try:
        result = subprocess.run(['wmic', 'logicaldisk', 'where', 'size>0', 'get', 'size,freespace', '/value'], 
                              capture_output=True, text=True, shell=True)
        
        total_size = 0
        free_space = 0
        
        lines = result.stdout.split('\n')
        for i, line in enumerate(lines):
            if 'FreeSpace=' in line and line.split('=')[1].strip():
                free_space += int(line.split('=')[1])
            elif 'Size=' in line and line.split('=')[1].strip():
                total_size += int(line.split('=')[1])
        
        if total_size > 0:
            used_space = total_size - free_space
            return (used_space / total_size) * 100
    except:
        pass
    return 0

def collect_system_metrics():
    """Collect real-time system metrics"""
    global current_metrics
    
    while True:
        try:
            # Get real-time metrics
            cpu = get_cpu_usage()
            memory = get_memory_usage()
            disk = get_disk_usage()
            
            # Update global metrics
            current_metrics = {
                'cpu_percent': cpu,
                'memory_percent': memory,
                'disk_percent': disk,
                'timestamp': datetime.now(),
                'network_sent': 0,
                'network_recv': 0
            }
            
            # Store in database
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO metrics 
                    (timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    current_metrics['timestamp'],
                    cpu,
                    memory,
                    disk,
                    0,
                    0
                ))
                
                conn.commit()
                conn.close()
                
                print("Live data - CPU:", round(cpu, 1), "% Memory:", round(memory, 1), "% Disk:", round(disk, 1), "%")
                
            except Exception as e:
                print("Database error:", str(e))
            
        except Exception as e:
            print("Metrics collection error:", str(e))
        
        time.sleep(2)  # Update every 2 seconds

def setup_database():
    """Setup database"""
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
        
        conn.commit()
        conn.close()
        print("Database setup completed")
    except Exception as e:
        print("Database setup error:", str(e))

# API Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/current')
def current_data():
    """Get current live metrics"""
    global current_metrics
    metrics = current_metrics.copy()
    metrics['timestamp'] = metrics['timestamp'].isoformat()
    return jsonify(metrics)

@app.route('/api/history')
def historical_data():
    """Get recent historical data"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, cpu_percent, memory_percent, disk_percent
            FROM metrics
            ORDER BY timestamp DESC
            LIMIT 50
        """)
        
        data = []
        for row in cursor.fetchall():
            data.append({
                'timestamp': row[0].isoformat(),
                'cpu': row[1],
                'memory': row[2],
                'disk': row[3]
            })
        
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/predictions')
def predictions():
    """Simple predictions based on current data"""
    global current_metrics
    
    # Simple prediction logic
    cpu_trend = current_metrics['cpu_percent'] + 5
    memory_trend = current_metrics['memory_percent'] + 3
    disk_trend = current_metrics['disk_percent'] + 1
    
    return jsonify({
        '1_hour': {
            'cpu': min(100, max(0, cpu_trend)),
            'memory': min(100, max(0, memory_trend)),
            'disk': min(100, max(0, disk_trend))
        },
        '6_hours': {
            'cpu': min(100, max(0, cpu_trend + 10)),
            'memory': min(100, max(0, memory_trend + 5)),
            'disk': min(100, max(0, disk_trend + 2))
        },
        '24_hours': {
            'cpu': min(100, max(0, cpu_trend + 15)),
            'memory': min(100, max(0, memory_trend + 8)),
            'disk': min(100, max(0, disk_trend + 3))
        }
    })

@app.route('/database')
def database_viewer():
    return render_template('database_viewer.html')

@app.route('/api/database-view')
def database_view_api():
    """API endpoint for database viewer"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM metrics")
        total = cursor.fetchone()[0]
        
        # Get latest 20 records
        cursor.execute("""
            SELECT id, timestamp, cpu_percent, memory_percent, disk_percent
            FROM metrics 
            ORDER BY timestamp DESC 
            LIMIT 20
        """)
        
        records = []
        for row in cursor.fetchall():
            records.append({
                'id': row[0],
                'timestamp': row[1].isoformat(),
                'cpu_percent': row[2],
                'memory_percent': row[3],
                'disk_percent': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'total': total,
            'records': records
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Setup database
    setup_database()
    
    # Start background monitoring thread
    monitor_thread = threading.Thread(target=collect_system_metrics, daemon=True)
    monitor_thread.start()
    
    print("🚀 Starting Real-time System Monitor")
    print("📊 Collecting live OS data every 2 seconds")
    print("🌐 Opening: http://localhost:5000")
    
    # Auto-open browser
    import webbrowser
    import threading
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)