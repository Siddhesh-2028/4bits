"""
Create VITA-Care tables in Supabase using SQL execution
This uses Supabase's RPC to execute SQL
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://fdmfyhsumhxokcobyscq.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Complete SQL to create all tables
CREATE_TABLES_SQL = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. PATIENTS TABLE
CREATE TABLE IF NOT EXISTS patients (
  pid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  username TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  phone TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE,
  dob DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. UPLOADS TABLE
CREATE TABLE IF NOT EXISTS uploads (
  upload_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pid UUID NOT NULL REFERENCES patients(pid) ON DELETE CASCADE,
  file_hash TEXT UNIQUE NOT NULL,
  file_name TEXT NOT NULL,
  file_size INTEGER NOT NULL,
  file_type TEXT NOT NULL,
  upload_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  extraction_status TEXT CHECK (extraction_status IN ('pending','success','failed')) DEFAULT 'pending',
  gemini_response_hash TEXT,
  error_message TEXT
);

-- 3. DOCTORS TABLE
CREATE TABLE IF NOT EXISTS doctors (
  did UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  doctor_name TEXT NOT NULL,
  doctor_id_external TEXT,
  pid UUID NOT NULL REFERENCES patients(pid) ON DELETE CASCADE,
  upload_id UUID REFERENCES uploads(upload_id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(pid, doctor_name, doctor_id_external)
);

-- 4. DRUGS TABLE
CREATE TABLE IF NOT EXISTS drugs (
  drug_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pid UUID NOT NULL REFERENCES patients(pid) ON DELETE CASCADE,
  upload_id UUID NOT NULL REFERENCES uploads(upload_id) ON DELETE CASCADE,
  drug_name TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(pid, drug_name, upload_id)
);

-- 5. DRUG SLOTS TABLE
CREATE TABLE IF NOT EXISTS drug_slots (
  slot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  drug_id UUID NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
  slot TEXT CHECK (slot IN ('morning','afternoon','night')) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(drug_id, slot)
);

-- 6. SCHEDULE TABLE
CREATE TABLE IF NOT EXISTS schedule (
  schedule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pid UUID NOT NULL REFERENCES patients(pid) ON DELETE CASCADE,
  did UUID REFERENCES doctors(did) ON DELETE SET NULL,
  upload_id UUID NOT NULL REFERENCES uploads(upload_id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- DISABLE RLS FOR API ACCESS
ALTER TABLE patients DISABLE ROW LEVEL SECURITY;
ALTER TABLE uploads DISABLE ROW LEVEL SECURITY;
ALTER TABLE doctors DISABLE ROW LEVEL SECURITY;
ALTER TABLE drugs DISABLE ROW LEVEL SECURITY;
ALTER TABLE drug_slots DISABLE ROW LEVEL SECURITY;
ALTER TABLE schedule DISABLE ROW LEVEL SECURITY;

-- CREATE INDEXES
CREATE INDEX IF NOT EXISTS idx_uploads_pid ON uploads(pid);
CREATE INDEX IF NOT EXISTS idx_drugs_pid ON drugs(pid);
CREATE INDEX IF NOT EXISTS idx_schedule_pid ON schedule(pid);
CREATE INDEX IF NOT EXISTS idx_doctors_pid ON doctors(pid);
CREATE INDEX IF NOT EXISTS idx_patients_username ON patients(username);
"""

def create_tables():
    """
    Create all tables using Supabase SQL execution
    """
    print("🔄 Connecting to Supabase...")
    print(f"   URL: {SUPABASE_URL}")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        print("\n📄 Executing SQL to create tables...")
        print("   This may take a moment...")
        
        # Execute SQL via Supabase's RPC
        result = supabase.rpc('exec_sql', {'query': CREATE_TABLES_SQL}).execute()
        
        print("✅ SQL executed successfully!")
        
        # Verify tables were created
        print("\n🔍 Verifying tables...")
        tables = ['patients', 'uploads', 'doctors', 'drugs', 'drug_slots', 'schedule']
        
        for table in tables:
            try:
                response = supabase.table(table).select("count", count="exact").limit(0).execute()
                print(f"   ✅ {table} - accessible (count: {response.count})")
            except Exception as e:
                print(f"   ❌ {table} - error: {e}")
        
        print("\n🎉 Database setup complete!")
        print("\n✨ You can now:")
        print("   1. Go to http://localhost:5173")
        print("   2. Sign up with your details")
        print("   3. Start using VITA-Care!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Alternative: Run SQL manually in Supabase Dashboard")
        print("   1. Go to: https://supabase.com/dashboard/project/fdmfyhsumhxokcobyscq/sql/new")
        print("   2. Copy the SQL from: backend/supabase_schema.sql")
        print("   3. Paste and click 'Run'")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("VITA-Care - Create Database Tables in Supabase")
    print("=" * 70)
    create_tables()
