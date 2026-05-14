import mysql.connector
import time

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dharanish@2505',
    'database': 'system_monitor'
}

def generate_live_sql_queries():
    """Generate and execute live SQL queries automatically"""
    
    print("🔴 AUTO-GENERATING LIVE SQL QUERIES")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create a view for live monitoring
        cursor.execute("DROP VIEW IF EXISTS live_monitor")
        cursor.execute("""
            CREATE VIEW live_monitor AS
            SELECT 
                id,
                DATE_FORMAT(timestamp, '%H:%i:%s') as Time,
                CONCAT(ROUND(cpu_percent, 1), '%') as CPU,
                CONCAT(ROUND(memory_percent, 1), '%') as Memory,
                CONCAT(ROUND(disk_percent, 1), '%') as Disk,
                CASE 
                    WHEN TIMESTAMPDIFF(SECOND, timestamp, NOW()) < 10 THEN 'LIVE'
                    ELSE 'OLD'
                END as Status
            FROM metrics 
            ORDER BY timestamp DESC 
            LIMIT 20
        """)
        
        print("✅ Created live_monitor view")
        
        # Create stored procedure for live data
        cursor.execute("DROP PROCEDURE IF EXISTS GetLiveData")
        cursor.execute("""
            CREATE PROCEDURE GetLiveData()
            BEGIN
                SELECT 'LIVE SYSTEM MONITOR' as Title, NOW() as Current_Time;
                
                SELECT * FROM live_monitor;
                
                SELECT 
                    'AVERAGES' as Type,
                    CONCAT(ROUND(AVG(cpu_percent), 1), '%') as Avg_CPU,
                    CONCAT(ROUND(AVG(memory_percent), 1), '%') as Avg_Memory,
                    COUNT(*) as Records
                FROM metrics 
                WHERE timestamp >= NOW() - INTERVAL 5 MINUTE;
            END
        """)
        
        print("✅ Created GetLiveData procedure")
        
        conn.commit()
        conn.close()
        
        print("\n🎯 NOW IN MYSQL WORKBENCH:")
        print("1. Open a new SQL tab")
        print("2. Copy and paste this query:")
        print("-" * 40)
        print("USE system_monitor;")
        print("CALL GetLiveData();")
        print("-" * 40)
        print("3. Keep pressing Ctrl+Enter every few seconds")
        print("4. Watch the result grid update with live data!")
        
        print("\n📊 OR use this simple query:")
        print("-" * 40)
        print("SELECT * FROM system_monitor.live_monitor;")
        print("-" * 40)
        
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    generate_live_sql_queries()