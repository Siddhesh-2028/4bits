"""
Migration: Add appointment_time to schedule table
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def run_migration():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL or SUPABASE_KEY not set.")
        return

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # SQL to add the column
    migration_sql = "ALTER TABLE schedule ADD COLUMN IF NOT EXISTS appointment_time TIMESTAMP WITH TIME ZONE;"
    
    print("🔄 Running migration: Adding appointment_time to schedule table...")
    try:
        # Check if we can execute SQL via RPC
        # Usually 'exec_sql' is a custom function created in the initial setup
        response = supabase.rpc('exec_sql', {'query': migration_sql}).execute()
        print("✅ Migration successful!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\n💡 Tip: You can also run this SQL manually in the Supabase SQL Editor:")
        print("ALTER TABLE schedule ADD COLUMN IF NOT EXISTS appointment_time TIMESTAMP WITH TIME ZONE;")

if __name__ == "__main__":
    run_migration()
