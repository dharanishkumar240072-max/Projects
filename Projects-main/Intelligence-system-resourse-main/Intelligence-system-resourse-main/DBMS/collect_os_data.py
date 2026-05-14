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
    print("🖥️ Collecting Real OS Data (Task Manager Style)")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Connected to MySQL database")
        print("📊 Collecting system data every 5 seconds...")
        print("Press Ctrl+C to stop\n")
        
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
            
            # Display like Task Manager
            print("Sample " + str(i+1) + ":")
            print("  CPU Usage: " + str(round(cpu_percent, 1)) + "%")
            print("  Memory: " + str(round(memory_percent, 1)) + "% (" + str(round(memory.used/1024/1024/1024, 1)) + " GB used)")
            print("  Disk C: " + str(round(disk_percent, 1)) + "% (" + str(round(disk.used/1024/1024/1024, 1)) + " GB used)")
            print("  Network: Sent " + str(round(network.bytes_sent/1024/1024, 1)) + " MB, Received " + str(round(network.bytes_recv/1024/1024, 1)) + " MB")
            print("  Time: " + str(datetime.now().strftime('%H:%M:%S')))
            print("-" * 40)
            
            time.sleep(5)  # Wait 5 seconds
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM metrics")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 5")
        recent_data = cursor.fetchall()
        
        print("\n✅ Data Collection Complete!")
        print("📊 Total records in database: " + str(total_count))
        print("\n🗄️ Recent 5 records in MySQL:")
        print("-" * 80)
        
        for row in recent_data:
            print("Time: " + str(row[1]) + " | CPU: " + str(row[2]) + "% | RAM: " + str(row[3]) + "% | Disk: " + str(row[4]) + "%")
        
        conn.close()
        
        print("\n🌐 Check MySQL Workbench now:")
        print("SELECT * FROM system_monitor.metrics ORDER BY timestamp DESC;")
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
        conn.close()
    except Exception as e:
        print("❌ Error: " + str(e))

if __name__ == "__main__":
    collect_real_os_data()