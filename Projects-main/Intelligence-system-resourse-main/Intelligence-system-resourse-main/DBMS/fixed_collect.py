import mysql.connector
import psutil
from datetime import datetime
import time

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dharanish@2505',
    'database': 'system_monitor'
}

def collect_real_os_data():
    """Collect real OS data like Task Manager"""
    print("Collecting Real OS Data")
    print("=" * 30)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Connected to MySQL database")
        print("Collecting system data...")
        print()
        
        for i in range(10):  # Collect 10 samples
            # Get real OS metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')
            network = psutil.net_io_counters()
            
            # Calculate percentages
            memory_percent = memory.percent
            disk_percent = (disk.used / disk.total) * 100
            
            # Insert into database
            cursor.execute("""
                INSERT INTO metrics 
                (timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                datetime.now(),
                cpu_percent,
                memory_percent,
                disk_percent,
                network.bytes_sent,
                network.bytes_recv
            ))
            
            conn.commit()
            
            # Display data
            print("Sample", i+1)
            print("CPU:", round(cpu_percent, 1), "%")
            print("Memory:", round(memory_percent, 1), "%")
            print("Disk:", round(disk_percent, 1), "%")
            print("Time:", datetime.now().strftime('%H:%M:%S'))
            print("-" * 30)
            
            time.sleep(3)  # Wait 3 seconds
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM metrics")
        total_count = cursor.fetchone()[0]
        
        print()
        print("Data Collection Complete!")
        print("Total records:", total_count)
        
        conn.close()
        
        print()
        print("Check MySQL Workbench:")
        print("SELECT * FROM system_monitor.metrics ORDER BY timestamp DESC;")
        
    except KeyboardInterrupt:
        print("Stopped by user")
        conn.close()
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    collect_real_os_data()