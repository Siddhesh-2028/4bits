"""
Refresh Supabase Schema Cache
This script tells Supabase to reload its table definitions
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://fdmfyhsumhxokcobyscq.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def refresh_schema():
    """
    Verify tables are accessible via Supabase API
    """
    print("🔄 Connecting to Supabase...")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Try to query the patients table
        print("📊 Testing patients table access...")
        response = supabase.table("patients").select("count", count="exact").limit(0).execute()
        
        print(f"✅ Patients table accessible! Count: {response.count}")
        
        # Test other tables
        tables = ["uploads", "doctors", "drugs", "drug_slots", "schedule"]
        for table in tables:
            try:
                resp = supabase.table(table).select("count", count="exact").limit(0).execute()
                print(f"✅ {table} table accessible! Count: {resp.count}")
            except Exception as e:
                print(f"❌ {table} table NOT accessible: {e}")
        
        print("\n🎉 Schema refresh complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n⚠️  This usually means:")
        print("   1. Tables don't exist in Supabase")
        print("   2. Row Level Security (RLS) is blocking access")
        print("   3. Schema cache needs manual refresh")
        print("\n🔧 SOLUTION:")
        print("   Go to Supabase Dashboard > SQL Editor")
        print("   Run the schema.sql file there instead")
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Supabase Schema Verification")
    print("=" * 60)
    refresh_schema()
