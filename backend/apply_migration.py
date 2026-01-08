"""
Apply database migration for phone number requirement
Run this to update existing database schema
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


def run_migration():
    """
    Apply migration to make phone required
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
        
        # Read migration file
        migration_path = os.path.join(os.path.dirname(__file__), "migration_phone_required.sql")
        
        with open(migration_path, "r", encoding="utf-8") as f:
            migration_sql = f.read()
        
        print("\n📄 Applying migration...")
        
        # Execute migration
        cursor = conn.cursor()
        
        try:
            cursor.execute(migration_sql)
            conn.commit()
            print("✅ Migration applied successfully!")
            
            # Verify changes
            cursor.execute("""
                SELECT column_name, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'patients' AND column_name = 'phone'
            """)
            result = cursor.fetchone()
            if result:
                print(f"\n📊 Phone column: nullable={result[1]}")
                if result[1] == 'NO':
                    print("✅ Phone is now REQUIRED")
                else:
                    print("⚠️ Phone is still nullable")
            
        except psycopg2.Error as e:
            if "already exists" in str(e) or "duplicate" in str(e).lower():
                print(f"⚠️ Migration partially applied (some changes already existed)")
                print(f"   Error: {e}")
                conn.rollback()
            else:
                raise
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Migration process complete!")
        
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
    print("VITA-Care Database Migration: Phone Requirement")
    print("=" * 60)
    run_migration()
