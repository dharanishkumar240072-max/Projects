import mysql.connector
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dharanish@2505',
    'database': 'system_monitor'
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Check metrics table
    cursor.execute("SELECT COUNT(*) FROM metrics")
    count = cursor.fetchone()[0]
    print("Total records in metrics table: " + str(count))
    
    # Get last 5 records
    cursor.execute("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 5")
    records = cursor.fetchall()
    
    print("\nLast 5 records:")
    print("-" * 80)
    for row in records:
        print("Time: " + str(row[1]) + " | CPU: " + str(row[2]) + "% | RAM: " + str(row[3]) + "% | Disk: " + str(row[4]) + "%")
    
    conn.close()
    print("\nData is being stored successfully!")
    
except Exception as e:
    print("Error: " + str(e))
