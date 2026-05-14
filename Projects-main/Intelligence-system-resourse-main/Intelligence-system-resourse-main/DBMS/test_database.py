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

def test_and_setup_database():
    """Test database connection and setup tables"""
    print("🔍 Testing MySQL connection...")
    
    try:
        # Test connection without database
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        print("✅ MySQL connection successful!")
        
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS system_monitor")
        cursor.execute("USE system_monitor")
        print("✅ Database 'system_monitor' ready")
        
        # Create tables
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
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME,
                type VARCHAR(50),
                message TEXT,
                severity VARCHAR(20)
            )
        """)
        
        conn.commit()
        print("✅ Tables created successfully")
        
        # Insert test data
        print("📊 Inserting test data...")
        for i in range(5):
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('C:').percent
            network = psutil.net_io_counters()
            
            cursor.execute("""
                INSERT INTO metrics 
                (timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                datetime.now(),
                cpu,
                memory,
                disk,
                network.bytes_sent,
                network.bytes_recv
            ))
            
            print("  Record " + str(i+1) + ": CPU=" + str(round(cpu,1)) + "%, RAM=" + str(round(memory,1)) + "%, Disk=" + str(round(disk,1)) + "%")
            time.sleep(1)
        
        conn.commit()
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM metrics")
        count = cursor.fetchone()[0]
        print("✅ " + str(count) + " records inserted successfully")
        
        # Show recent data
        cursor.execute("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 3")
        rows = cursor.fetchall()
        
        print("\n📋 Recent data in database:")
        print("-" * 60)
        for row in rows:
            print("Time: " + str(row[1]) + " | CPU: " + str(round(row[2],1)) + "% | RAM: " + str(round(row[3],1)) + "% | Disk: " + str(round(row[4],1)) + "%")
        
        conn.close()
        print("\n✅ Database test completed successfully!")
        print("🌐 Now check MySQL Workbench: SELECT * FROM system_monitor.metrics;")
        
        return True
        
    except mysql.connector.Error as err:
        print("❌ MySQL Error: " + str(err))
        return False
    except Exception as e:
        print("❌ Error: " + str(e))
        return False

if __name__ == "__main__":
    print("🗄️ MySQL Database Test & Setup")
    print("=" * 40)
    
    if test_and_setup_database():
        print("\n🎉 Success! Your database is ready.")
        print("📊 Check MySQL Workbench now - you should see data!")
    else:
        print("\n❌ Database setup failed. Check MySQL connection.")