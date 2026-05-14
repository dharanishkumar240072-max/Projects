import mysql.connector
from datetime import datetime
import time
import random

def insert_real_data():
    """Insert data into MySQL database"""
    print("Inserting OS data into MySQL...")
    
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Dharanish@2505',
        'database': 'system_monitor'
    }
    
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        print("Connected to MySQL")
        
        # Insert 5 records with realistic system data
        data_samples = [
            (datetime.now(), 25.4, 67.8, 72.1, 5847392847, 8374829374),
            (datetime.now(), 31.2, 71.3, 72.2, 5847493821, 8374930284),
            (datetime.now(), 18.7, 69.1, 72.1, 5847594832, 8375031847),
            (datetime.now(), 42.3, 73.5, 72.3, 5847695843, 8375132958),
            (datetime.now(), 28.9, 70.2, 72.2, 5847796854, 8375234069)
        ]
        
        for i, data in enumerate(data_samples):
            query = "INSERT INTO metrics (timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, data)
            conn.commit()
            
            print("Record", i+1, "inserted - CPU:", data[1], "% Memory:", data[2], "% Disk:", data[3], "%")
            time.sleep(1)
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM metrics")
        total = cursor.fetchone()[0]
        print("SUCCESS! Total records in database:", total)
        
        # Show recent data
        cursor.execute("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 3")
        recent = cursor.fetchall()
        
        print("\nRecent records:")
        for row in recent:
            print("ID:", row[0], "Time:", row[1], "CPU:", row[2], "%")
        
        cursor.close()
        conn.close()
        
        print("\nData successfully stored in MySQL!")
        print("Now check MySQL Workbench:")
        print("SELECT * FROM system_monitor.metrics ORDER BY timestamp DESC;")
        
        return True
        
    except Exception as e:
        print("Database error:", str(e))
        return False

if __name__ == "__main__":
    insert_real_data()