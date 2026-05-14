import mysql.connector
from datetime import datetime
import random

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dharanish@2505',
    'database': 'system_monitor'
}

def insert_test_data():
    """Insert test data into database"""
    print("🔍 Testing MySQL connection...")
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        
        # Insert 5 test records
        print("📊 Inserting test data...")
        
        for i in range(5):
            # Generate sample data
            cpu = round(random.uniform(20, 80), 1)
            memory = round(random.uniform(40, 90), 1)
            disk = round(random.uniform(50, 95), 1)
            network_sent = random.randint(1000000, 9999999)
            network_recv = random.randint(1000000, 9999999)
            
            cursor.execute("""
                INSERT INTO metrics 
                (timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                datetime.now(),
                cpu,
                memory,
                disk,
                network_sent,
                network_recv
            ))
            
            print("  Record " + str(i+1) + " inserted")
        
        conn.commit()
        
        # Check data
        cursor.execute("SELECT COUNT(*) FROM metrics")
        count = cursor.fetchone()[0]
        print("✅ Total records: " + str(count))
        
        # Show recent data
        cursor.execute("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 3")
        rows = cursor.fetchall()
        
        print("\n📋 Recent data:")
        print("-" * 50)
        for row in rows:
            print("ID: " + str(row[0]) + " | Time: " + str(row[1]) + " | CPU: " + str(row[2]) + "%")
        
        conn.close()
        print("\n✅ SUCCESS! Data inserted into MySQL database")
        print("🌐 Check MySQL Workbench: SELECT * FROM system_monitor.metrics;")
        
    except Exception as e:
        print("❌ Error: " + str(e))

if __name__ == "__main__":
    print("🗄️ Simple Database Test")
    print("=" * 30)
    insert_test_data()