import mysql.connector
import time
import os
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dharanish@2505',
    'database': 'system_monitor'
}

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_live_data():
    """Show live updating MySQL data"""
    print("🔴 LIVE MySQL Data Monitor")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            clear_screen()
            
            print("🔴 LIVE MySQL Data Monitor - " + datetime.now().strftime('%H:%M:%S'))
            print("=" * 60)
            
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                
                # Get total records
                cursor.execute("SELECT COUNT(*) FROM metrics")
                total = cursor.fetchone()[0]
                
                # Get latest 10 records
                cursor.execute("""
                    SELECT timestamp, cpu_percent, memory_percent, disk_percent
                    FROM metrics 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """)
                
                rows = cursor.fetchall()
                
                print("📊 Total Records in Database:", total)
                print("🕒 Last Updated:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                print()
                print("📈 LIVE SYSTEM DATA (Latest 10 records):")
                print("-" * 60)
                print("Time".ljust(20), "CPU%".ljust(8), "Memory%".ljust(10), "Disk%".ljust(8))
                print("-" * 60)
                
                for row in rows:
                    timestamp = row[0].strftime('%H:%M:%S')
                    cpu = str(round(row[1], 1)) + "%"
                    memory = str(round(row[2], 1)) + "%"
                    disk = str(round(row[3], 1)) + "%"
                    
                    print(timestamp.ljust(20), cpu.ljust(8), memory.ljust(10), disk.ljust(8))
                
                # Show current averages
                cursor.execute("""
                    SELECT AVG(cpu_percent), AVG(memory_percent), AVG(disk_percent)
                    FROM metrics 
                    WHERE timestamp >= NOW() - INTERVAL 5 MINUTE
                """)
                
                avg_row = cursor.fetchone()
                if avg_row[0]:
                    print()
                    print("📊 5-Minute Averages:")
                    print("-" * 30)
                    print("CPU Average:", round(avg_row[0], 1), "%")
                    print("Memory Average:", round(avg_row[1], 1), "%")
                    print("Disk Average:", round(avg_row[2], 1), "%")
                
                # Show alerts
                if avg_row[0] and avg_row[0] > 80:
                    print()
                    print("🚨 HIGH CPU USAGE ALERT!")
                
                if avg_row[1] and avg_row[1] > 85:
                    print("🚨 HIGH MEMORY USAGE ALERT!")
                
                conn.close()
                
                print()
                print("🔄 Refreshing every 3 seconds... (Ctrl+C to stop)")
                
            except Exception as e:
                print("Database error:", str(e))
            
            time.sleep(3)  # Refresh every 3 seconds
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Live monitor stopped!")

if __name__ == "__main__":
    show_live_data()