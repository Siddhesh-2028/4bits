# 🚀 STEP-BY-STEP: Create Database Tables in Supabase

## 📋 What You Need To Do

Since the tables don't exist yet, you need to create them in Supabase's SQL Editor.

---

## ✅ Step 1: Open Supabase SQL Editor

Click this link:  
**https://supabase.com/dashboard/project/fdmfyhsumhxokcobyscq/sql/new**

---

## ✅ Step 2: Copy This SQL

```sql
-- VITA-Care Database Schema - Copy ALL of this

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. PATIENTS TABLE
CREATE TABLE patients (
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
CREATE TABLE uploads (
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
CREATE TABLE doctors (
  did UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  doctor_name TEXT NOT NULL,
  doctor_id_external TEXT,
  pid UUID NOT NULL REFERENCES patients(pid) ON DELETE CASCADE,
  upload_id UUID REFERENCES uploads(upload_id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(pid, doctor_name, doctor_id_external)
);

-- 4. DRUGS TABLE
CREATE TABLE drugs (
  drug_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pid UUID NOT NULL REFERENCES patients(pid) ON DELETE CASCADE,
  upload_id UUID NOT NULL REFERENCES uploads(upload_id) ON DELETE CASCADE,
  drug_name TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(pid, drug_name, upload_id)
);

-- 5. DRUG SLOTS TABLE
CREATE TABLE drug_slots (
  slot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  drug_id UUID NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
  slot TEXT CHECK (slot IN ('morning','afternoon','night')) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(drug_id, slot)
);

-- 6. SCHEDULE TABLE
CREATE TABLE schedule (
  schedule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pid UUID NOT NULL REFERENCES patients(pid) ON DELETE CASCADE,
  did UUID REFERENCES doctors(did) ON DELETE SET NULL,
  upload_id UUID NOT NULL REFERENCES uploads(upload_id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Disable RLS for API access (development mode)
ALTER TABLE patients DISABLE ROW LEVEL SECURITY;
ALTER TABLE uploads DISABLE ROW LEVEL SECURITY;
ALTER TABLE doctors DISABLE ROW LEVEL SECURITY;
ALTER TABLE drugs DISABLE ROW LEVEL SECURITY;
ALTER TABLE drug_slots DISABLE ROW LEVEL SECURITY;
ALTER TABLE schedule DISABLE ROW LEVEL SECURITY;

-- Create indexes for performance
CREATE INDEX idx_uploads_pid ON uploads(pid);
CREATE INDEX idx_drugs_pid ON drugs(pid);
CREATE INDEX idx_schedule_pid ON schedule(pid);
CREATE INDEX idx_doctors_pid ON doctors(pid);
CREATE INDEX idx_patients_username ON patients(username);
```

---

## ✅ Step 3: Paste & Run

1. **Paste** the entire SQL into the editor
2. **Click "Run"** button (bottom right)
3. Wait for "Success" message

---

## ✅ Step 4: Verify Tables Were Created

After running, you should see 6 new tables in your Supabase project:
- ✅ patients
- ✅ uploads  
- ✅ doctors
- ✅ drugs
- ✅ drug_slots
- ✅ schedule

Check the left sidebar under "Tables" - you should see all 6!

---

## 🧪 Step 5: Test Signup

1. Go to **http://localhost:5173**
2. Click **"Sign Up"**
3. Fill in:
   - Full Name: Your Name
   - Username: yourusername
   - Mobile Number: 1234567890
   - Password: test123
4. Click **"Create Account"**

**It should work now!** ✨

---

## ❌ If You Get Errors

### Error: "relation already exists"
This means some tables already exist. That's OK! The errors won't break anything.

### Error: "permission denied"
Your Supabase key might not have permission. Use the dashboard instead of Python scripts.

### Still Getting "Could not find table"?
After running the SQL, wait 10 seconds, then refresh your browser at http://localhost:5173

---

## 📞 After Creating Tables

Once tables are created, let me know and I'll help you:
- Test the signup/login flow
- Implement the prescription upload feature
- Add medication schedule display

---

**Created**: 2026-01-08  
**Status**: Ready to run!
