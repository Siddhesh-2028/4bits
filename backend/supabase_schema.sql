-- VITA-Care Database Schema for Supabase
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/fdmfyhsumhxokcobyscq/sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if needed (CAUTION: This will delete data!)
-- Uncomment the following lines if you need to recreate tables
-- DROP TABLE IF EXISTS drug_slots CASCADE;
-- DROP TABLE IF EXISTS drugs CASCADE;
-- DROP TABLE IF EXISTS schedule CASCADE;
-- DROP TABLE IF EXISTS doctors CASCADE;
-- DROP TABLE IF EXISTS uploads CASCADE;
-- DROP TABLE IF EXISTS patients CASCADE;

-- ================================================
-- 1. PATIENTS TABLE
-- ================================================
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

-- ================================================
-- 2. UPLOADS TABLE (Audit Trail)
-- ================================================
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

-- ================================================
-- 3. DOCTORS TABLE
-- ================================================
CREATE TABLE IF NOT EXISTS doctors (
  did UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  doctor_name TEXT NOT NULL,
  doctor_id_external TEXT,
  pid UUID NOT NULL REFERENCES patients(pid) ON DELETE CASCADE,
  upload_id UUID REFERENCES uploads(upload_id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(pid, doctor_name, doctor_id_external)
);

-- ================================================
-- 4. DRUGS TABLE
-- ================================================
CREATE TABLE IF NOT EXISTS drugs (
  drug_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pid UUID NOT NULL REFERENCES patients(pid) ON DELETE CASCADE,
  upload_id UUID NOT NULL REFERENCES uploads(upload_id) ON DELETE CASCADE,
  drug_name TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(pid, drug_name, upload_id)
);

-- ================================================
-- 5. DRUG SLOTS TABLE
-- ================================================
CREATE TABLE IF NOT EXISTS drug_slots (
  slot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  drug_id UUID NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
  slot TEXT CHECK (slot IN ('morning','afternoon','night')) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(drug_id, slot)
);

-- ================================================
-- 6. SCHEDULE TABLE
-- ================================================
CREATE TABLE IF NOT EXISTS schedule (
  schedule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pid UUID NOT NULL REFERENCES patients(pid) ON DELETE CASCADE,
  did UUID REFERENCES doctors(did) ON DELETE SET NULL,
  upload_id UUID NOT NULL REFERENCES uploads(upload_id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================================
-- INDEXES FOR PERFORMANCE
-- ================================================
CREATE INDEX IF NOT EXISTS idx_uploads_pid ON uploads(pid);
CREATE INDEX IF NOT EXISTS idx_uploads_status ON uploads(extraction_status);
CREATE INDEX IF NOT EXISTS idx_drugs_pid ON drugs(pid);
CREATE INDEX IF NOT EXISTS idx_drugs_upload ON drugs(upload_id);
CREATE INDEX IF NOT EXISTS idx_schedule_pid ON schedule(pid);
CREATE INDEX IF NOT EXISTS idx_doctors_pid ON doctors(pid);
CREATE INDEX IF NOT EXISTS idx_patients_username ON patients(username);

-- ================================================
-- DISABLE ROW LEVEL SECURITY (RLS) FOR API ACCESS
-- ================================================
-- ⚠️ WARNING: This disables security. For production, enable RLS with proper policies!
-- But for development/demo, this allows the API to work

ALTER TABLE patients DISABLE ROW LEVEL SECURITY;
ALTER TABLE uploads DISABLE ROW LEVEL SECURITY;
ALTER TABLE doctors DISABLE ROW LEVEL SECURITY;
ALTER TABLE drugs DISABLE ROW LEVEL SECURITY;
ALTER TABLE drug_slots DISABLE ROW LEVEL SECURITY;
ALTER TABLE schedule DISABLE ROW LEVEL SECURITY;

-- ================================================
-- TRIGGER FOR UPDATED_AT TIMESTAMP
-- ================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_patients_updated_at ON patients;
CREATE TRIGGER update_patients_updated_at
    BEFORE UPDATE ON patients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- VERIFICATION
-- ================================================
-- Check that all tables were created
SELECT
    tablename,
    schemaname
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('patients', 'uploads', 'doctors', 'drugs', 'drug_slots', 'schedule')
ORDER BY tablename;
