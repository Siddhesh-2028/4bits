# VITA-Care Setup - Authentication & Prescription Upload

## ✅ Completed So Far

### Backend
- ✅ Database schema created (`schema.sql`)
- ✅ Supabase client configured (`supabase_client.py`)
- ✅ Authentication module with JWT (`auth.py`)
- ✅ User registration and login endpoints (`/api/register`, `/api/login`)
- ✅ Protected endpoints with JWT middleware
- ✅ Password hashing with bcrypt
- ✅ Models for auth and prescription upload

### Frontend
- ✅ Auth component with login/signup UI
- ✅ Protected dashboard with authentication
- ✅ JWT token storage in localStorage
- ✅ Auto-logout on session expiry
- ✅ Beautiful, modern UI design

---

## 🔧 Next Steps (Manual Configuration Required)

### 1. Set Up .env File

Create a `.env` file in the `backend/` directory with the following content:

```env
# Gemini API Key (Get from https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase Credentials
SUPABASE_URL=https://fdmfyhsumhxokcobyscq.supabase.co

# Get the anon key from Supabase Dashboard:
# Go to: Project Settings > API > Project API keys > "anon" (public)
SUPABASE_KEY=your_supabase_anon_key_here

SUPABASE_PASSWORD=gGngRRXW4odtxDLH

# JWT Secret (must be at least 32 characters)
JWT_SECRET=vita-care-hackathon-2026-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### 2. Get Supabase Anon Key

1. Go to your Supabase project: https://supabase.com/dashboard
2. Click on your project (fdmfyhsumhxokcobyscq)
3. Go to **Settings** (gear icon) → **API**
4. Copy the **`anon`** key (under "Project API keys")
5. Paste it into your `.env` file as `SUPABASE_KEY`

### 3. Verify Database Tables

Run the database initialization script to create tables:

```bash
cd backend
python init_db.py
```

You should see output like:
```
✅ Database schema created successfully!
📊 Created tables:
   - patients
   - uploads
   - doctors
   - drugs
   - drug_slots
   - schedule
```

### 4. Test Backend

Start the FastAPI backend:

```bash
cd backend
python main.py
```

Visit `http://localhost:8000` - you should see:
```json
{"status": "VITA-Care Backend Operational", "version": "2.0.0"}
```

Test Supabase connection:
```bash
python supabase_client.py
```

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` - you should see the login/signup page!

---

## 🧪 Testing Authentication

### Register a New User
1. Open http://localhost:5173
2. Click "Sign Up"
3. Fill in:
   - Full Name: Test User
   - Username: testuser
   - Password: test123
4. Click "Create Account"

You should be logged in and see the dashboard!

### Login
1. Click "Logout" (top right)
2. Click "Login"
3. Enter username: `testuser`, password: `test123`
4. Click "Login"

---

## 📁 Project Structure

```
VITA-CARE/
├── backend/
│   ├── .env                    # ⚠️ YOU NEED TO CREATE THIS
│   ├── .env.example
│   ├── schema.sql             # Database schema
│   ├── init_db.py             # Database initialization script
│   ├── supabase_client.py     # Supabase connection
│   ├── auth.py                # JWT & password hashing
│   ├── models.py              # Pydantic models
│   ├── main.py                # FastAPI app
│   ├── agent.py               # Voice agent logic
│   └── tools.py               # Agent tools
│
└── frontend/
    ├── src/
    │   ├── App.tsx            # Main app with auth routing
    │   ├── components/
    │   │   ├── Auth.tsx       # Login/Signup component
    │   │   ├── VoiceControlPanel.tsx
    │   │   ├── Transcript.tsx
    │   │   └── ToolLog.tsx
    │   ├── index.css
    │   └── main.tsx
    └── package.json
```

##🚀 What's Next?

After authentication is working, we'll implement:

1. **Prescription Upload Feature**
   - File upload UI (drag & drop)
   - Image/PDF processing
   - Gemini extraction
   - Database storage

2. **Medication Schedule Display**
   - Morning/Afternoon/Night slots
   - Doctor information
   - Medication cards

3. **Voice Agent Integration**
   - Query medications via voice
   - Set reminders
   - Prescription history

---

## ⚠️ Important Security Notes

- Never commit `.env` file to Git (it's already in `.gitignore`)
- Change `JWT_SECRET` before production deployment
- Use environment-specific API keys (dev vs production)
- Enable Row Level Security (RLS) in Supabase for production

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `SUPABASE_KEY is not set` | Create `.env` file with proper keys |
| Database connection fails | Check `SUPABASE_PASSWORD` and run `init_db.py` |
| JWT errors | Ensure `JWT_SECRET` is at least 32 characters |
| CORS errors | Backend must run on port 8000, frontend on 5173 |
| Login fails after signup | Check backend terminal for error logs |

---

## 📊 API Endpoints

### Public Endpoints
- `POST /api/register` - Create new user account
- `POST /api/login` - Login and get JWT token

### Protected Endpoints (Require JWT)
- `GET /api/profile` - Get current user profile
- `POST /api/chat` - Voice agent interaction

### Coming Soon
- `POST /api/upload_prescription` - Upload prescription file
- `GET /api/medications` - Get medication schedule

---

**Created by:** VITA-Care Development Team  
**Date:** 2026-01-08  
**Status:** ✅ Backend Authentication Complete | 🔄 Prescription Upload In Progress
