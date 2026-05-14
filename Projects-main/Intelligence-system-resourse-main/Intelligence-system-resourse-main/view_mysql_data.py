import mysql.connector
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dharanish@2505',
    'database': 'system_monitor'
}

print("=" * 100)
print("MYSQL DATABASE DATA VIEWER")
print("=" * 100)

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Check total records
    cursor.execute("SELECT COUNT(*) FROM metrics")
    total = cursor.fetchone()[0]
    print("\nTotal records in database: " + str(total))
    
    if total == 0:
        print("\nNo data found! Backend needs to run for at least 30 seconds to collect data.")
    else:
        # Get last 10 records
        print("\n" + "=" * 100)
        print("LAST 10 RECORDS FROM MYSQL:")
        print("=" * 100)
        
        cursor.execute("""
            SELECT id, timestamp, cpu_percent, memory_percent, disk_percent, 
                   network_sent, network_recv 
            FROM metrics 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        
        records = cursor.fetchall()
        
        print("\n{:<5} {:<20} {:<10} {:<12} {:<10} {:<15} {:<15}".format(
            "ID", "Timestamp", "CPU %", "Memory %", "Disk %", "Net Sent(MB)", "Net Recv(MB)"
        ))
        print("-" * 100)
        
        for row in records:
            net_sent = round(row[5] / 1024 / 1024, 2)
            net_recv = round(row[6] / 1024 / 1024, 2)
            
            print("{:<5} {:<20} {:<10} {:<12} {:<10} {:<15} {:<15}".format(
                row[0],
                str(row[1]),
                str(round(row[2], 1)),
                str(round(row[3], 1)),
                str(round(row[4], 1)),
                str(net_sent),
                str(net_recv)
            ))
    
    # Check alerts
    cursor.execute("SELECT COUNT(*) FROM alerts")
    alert_count = cursor.fetchone()[0]
    
    print("\n" + "=" * 100)
    print("ALERTS: " + str(alert_count) + " total")
    print("=" * 100)
    
    if alert_count > 0:
        cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 5")
        alerts = cursor.fetchall()
        
        for alert in alerts:
            print("\n[" + alert[4] + "] " + alert[2] + " - " + alert[3])
            print("Time: " + str(alert[1]))
    else:
        print("No alerts found.")
    
    conn.close()
    print("\n" + "=" * 100)
    print("Data fetched successfully from MySQL!")
    print("=" * 100)
    
except Exception as e:
    print("\nError: " + str(e))
    print("\nMake sure:")
    print("1. MySQL server is running")
    print("2. backend.py has been running for at least 30 seconds")
    print("3. Database password is correct")

input("\nPress Enter to exit...")
