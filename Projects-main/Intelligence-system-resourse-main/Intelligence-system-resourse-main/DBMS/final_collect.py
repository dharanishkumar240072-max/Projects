import mysql.connector
import psutil
from datetime import datetime
import time

def collect_and_store_data():
    """Collect real OS data and store in MySQL"""
    print("Starting OS Data Collection...")
    
    # Database config
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Dharanish@2505',
        'database': 'system_monitor'
    }
    
    try:
        # Connect to database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        print("Connected to database")
        
        # Collect 5 samples
        for i in range(5):
            print("Collecting sample", i+1)
            
            # Get system data
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')
            net = psutil.net_io_counters()
            
            mem_percent = memory.percent
            disk_percent = (disk.used / disk.total) * 100
            timestamp = datetime.now()
            
            # Insert data using individual values
            query = "INSERT INTO metrics (timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (timestamp, cpu, mem_percent, disk_percent, net.bytes_sent, net.bytes_recv)
            
            cursor.execute(query, values)
            conn.commit()
            
            print("CPU:", round(cpu, 1), "% | Memory:", round(mem_percent, 1), "% | Disk:", round(disk_percent, 1), "%")
            
            time.sleep(2)
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM metrics")
        count = cursor.fetchone()[0]
        print("SUCCESS! Total records:", count)
        
        # Show recent data
        cursor.execute("SELECT timestamp, cpu_percent, memory_percent, disk_percent FROM metrics ORDER BY timestamp DESC LIMIT 3")
        rows = cursor.fetchall()
        
        print("\nRecent data:")
        for row in rows:
            print("Time:", row[0], "CPU:", row[1], "% Memory:", row[2], "% Disk:", row[3], "%")
        
        cursor.close()
        conn.close()
        
        print("\nData stored successfully!")
        print("Check MySQL Workbench: SELECT * FROM system_monitor.metrics;")
        
    except Exception as e:
        print("Error occurred:", str(e))
        print("Error type:", type(e).__name__)

if __name__ == "__main__":
    collect_and_store_data()