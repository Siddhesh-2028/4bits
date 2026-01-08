# 🔧 FIX: Supabase API Access Error

## Problem
You're getting error: `"Could not find the table 'public.patients' in the schema cache"` (PGRST205)

**Root Cause**: Row Level Security (RLS) is enabled by default in Supabase, blocking API access.

---

## ✅ SOLUTION (2 minutes)

### Step 1: Open Supabase SQL Editor
Go to: **https://supabase.com/dashboard/project/fdmfyhsumhxokcobyscq/sql/new**

### Step 2: Copy & Paste This SQL

```sql
-- Disable Row Level Security to allow API access

ALTER TABLE patients DISABLE ROW LEVEL SECURITY;
ALTER TABLE uploads DISABLE ROW LEVEL SECURITY;
ALTER TABLE doctors DISABLE ROW LEVEL SECURITY;
ALTER TABLE drugs DISABLE ROW LEVEL SECURITY;
ALTER TABLE drug_slots DISABLE ROW LEVEL SECURITY;
ALTER TABLE schedule DISABLE ROW LEVEL SECURITY;
```

### Step 3: Click "Run" (or press Cmd/Ctrl + Enter)

You should see: `Success. No rows returned`

---

## 🧪 Verify It Worked

### Option 1: Try Signup Again
1. Go to http://localhost:5173  
2. Fill in the signup form
3. Click "Create Account"
4. It should work now! ✅

### Option 2: Run Verification Script
```bash
cd backend
python verify_schema.py
```

You should see all tables marked as "accessible"

---

## ⚠️ Important Notes

**Why disable RLS?**
- For development/demo, RLS blocks the API from working
- In production, you'd enable RLS and create security policies

**Is this secure for demo?**
- For local development: ✅ Yes, fine
- For production: ❌ No, enable RLS with proper policies

---

## 🚀 After the Fix

Once you run that SQL, your signup should work perfectly!

![Signup Error](file:///C:/Users/nithi/.gemini/antigravity/brain/81bbf534-eebe-45ae-a707-817fe8bbad99/uploaded_image_1767869064505.png)

This error will be gone! ✨
