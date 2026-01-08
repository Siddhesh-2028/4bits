"""
Database Initialization Script for VITA-Care
Runs the schema.sql file on Supabase PostgreSQL
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Parse Supabase connection string
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "gGngRRXW4odtxDLH")
SUPABASE_HOST = "db.fdmfyhsumhxokcobyscq.supabase.co"
SUPABASE_PORT = 5432
SUPABASE_DATABASE = "postgres"
SUPABASE_USER = "postgres"


def initialize_database():
    """
    Connect to Supabase and execute schema.sql
    """
    print("🔄 Connecting to Supabase PostgreSQL...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=SUPABASE_HOST,
            port=SUPABASE_PORT,
            database=SUPABASE_DATABASE,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD
        )
        
        print("✅ Connected to Supabase successfully!")
        
        # Read schema file
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        
        print("\n📄 Executing schema.sql...")
        
        # Execute schema
        cursor = conn.cursor()
        cursor.execute(schema_sql)
        conn.commit()
        
        print("✅ Database schema created successfully!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("\n📊 Created tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database initialization complete!")
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        print(f"   Error code: {e.pgcode}")
        print(f"   Error details: {e.pgerror}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("VITA-Care Database Initialization")
    print("=" * 60)
    initialize_database()
