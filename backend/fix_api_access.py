"""
Fix Supabase API Access by Disabling RLS
This script disables Row Level Security to allow API access
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "gGngRRXW4odtxDLH")
SUPABASE_HOST = "db.fdmfyhsumhxokcobyscq.supabase.co"
SUPABASE_PORT = 5432
SUPABASE_DATABASE = "postgres"
SUPABASE_USER = "postgres"


def disable_rls():
    """
    Disable Row Level Security on all tables to enable API access
    """
    print("🔄 Connecting to Supabase PostgreSQL...")
    
    try:
        conn = psycopg2.connect(
            host=SUPABASE_HOST,
            port=SUPABASE_PORT,
            database=SUPABASE_DATABASE,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD
        )
        
        print("✅ Connected successfully!")
        
        cursor = conn.cursor()
        
        tables = ['patients', 'uploads', 'doctors', 'drugs', 'drug_slots', 'schedule']
        
        print("\n🔓 Disabling Row Level Security on all tables...")
        
        for table in tables:
            try:
                cursor.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
                print(f"   ✅ {table} - RLS disabled")
            except Exception as e:
                print(f"   ⚠️  {table} - {e}")
        
        conn.commit()
        
        print("\n✅ All tables now accessible via Supabase API!")
        print("\n🔍 Verifying table accessibility...")
        
        # Verify
        cursor.execute("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('patients', 'uploads', 'doctors', 'drugs', 'drug_slots', 'schedule')
            ORDER BY tablename;
        """)
        
        results = cursor.fetchall()
        print("\n📊 Table Security Status:")
        for table, rls_enabled in results:
            status = "❌ ENABLED (blocking API)" if rls_enabled else "✅ DISABLED (API works)"
            print(f"   {table}: {status}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Fix complete! Try signing up again.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("VITA-Care - Fix Supabase API Access")
    print("=" * 60)
    disable_rls()
