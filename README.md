<h1 align="center">VITA-CARE</h1>

<p align="center">
  <strong>Voice-Integrated Task-Autonomous Care Coordination Agent</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Node.js-18+-339933?style=flat-square&logo=node.js&logoColor=white" alt="Node.js 18+">
  <img src="https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript">
</p>

## 📋 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Domain Relevance](#-domain-relevance)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Project Structure](#-project-structure)
- [Quick Start with Docker](#-quick-start-with-docker)
- [Manual Setup (Development)](#-manual-setup-development)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Usage Guide](#-usage-guide)
- [Assumptions](#-assumptions)
- [Known Limitations](#-known-limitations)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

## 🏥 Overview

**VITA-CARE** (Voice-Integrated Task-Autonomous Care Coordination Agent) is a multi-service healthcare coordination application designed to streamline administrative healthcare tasks through voice interaction and AI-powered automation. The platform enables patients to manage appointments, prescriptions, and medication reminders using natural language voice commands.

The system leverages Google Gemini AI to power autonomous agents that handle scheduling, booking, notifications, and medication reminders. Users can interact with the system through a modern web interface featuring voice recognition capabilities, while the backend orchestrates complex workflows across multiple specialised agents.

VITA-CARE integrates with WhatsApp to deliver medication reminders directly to patients' phones, ensuring timely adherence to prescribed medications. The application follows a microservices architecture with three core services: a React frontend, a FastAPI backend, and a Node.js WhatsApp bridge.

> [!CAUTION]
> **Medical Disclaimer:** VITA-CARE is an **administrative coordination tool only**. It does **NOT** provide medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for medical decisions. The AI agents are designed solely for scheduling, reminders, and administrative tasks.

## 🎯 Problem Statement

Healthcare coordination presents significant challenges for patients:

- **Fragmented Appointment Management**: Patients often struggle to track multiple appointments across different healthcare providers, leading to missed visits and delayed care.

- **Medication Non-Adherence**: Forgetting to take medications at prescribed times is a widespread issue, particularly for patients managing multiple prescriptions. This leads to poorer health outcomes and increased healthcare costs.

- **Complex Administrative Workflows**: Scheduling appointments, managing prescriptions, and coordinating care requires navigating multiple systems and making numerous phone calls.

**Why Voice-Integrated Autonomous Agents Matter:**

Voice interfaces provide a natural, accessible way for patients to interact with healthcare systems without navigating complex UIs. Autonomous AI agents can handle routine administrative tasks—such as checking doctor availability, booking appointments, and sending reminders—without human intervention, freeing up both patients and healthcare staff.

**Target Users:** Patients who need to manage appointments, track medications, and receive timely reminders to support their healthcare routines.

## 🏛️ Domain Relevance

VITA-CARE addresses a critical gap in modern healthcare: the automation of non-clinical administrative tasks. While clinical care requires human expertise, many surrounding workflows—scheduling, reminders, prescription management—are repetitive and time-consuming.

**Why Automation Matters in Healthcare Administration:**

1. **Reduced Administrative Burden**: Patients spend less time on phone calls and form-filling, focusing instead on their health.

2. **Improved Medication Adherence**: Automated reminders via WhatsApp reach patients on a platform they already use daily.

3. **Accessibility**: Voice interfaces make healthcare coordination accessible to users who may struggle with traditional web forms.

4. **Scalability**: AI-powered agents can handle thousands of routine requests simultaneously, unlike human administrative staff.

5. **Consistency**: Automated systems provide reliable, consistent service without fatigue or human error in routine tasks.

## 🏗️ Architecture

VITA-CARE follows a microservices architecture with three core services communicating through a Docker network.

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER'S BROWSER                                 │
│                    (Voice Input via Web Speech API)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND SERVICE (Port 80)                          │
│                   React + TypeScript + Vite + TailwindCSS                   │
│                         Served via Nginx Reverse Proxy                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND SERVICE (Port 8000)                         │
│                         FastAPI + Python + Gemini AI                        │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                           AGENT ROUTER                                 │ │
│  │  Routes requests to appropriate specialised agent based on intent      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                │              │              │               │              │
│                ▼              ▼              ▼               ▼              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────────────┐ │
│  │  Scheduling  │ │   Booking    │ │ Notification │ │ Medication Reminder │ │
│  │    Agent     │ │    Agent     │ │    Agent     │ │       Agent         │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
           │                                                      │
           ▼                                                      ▼
┌─────────────────────────┐                   ┌──────────────────────────────┐
│   SUPABASE (PostgreSQL) │                   │  WHATSAPP SERVICE (Port 3001)│
│                         │                   │  Node.js + whatsapp-web.js   │
│  • patients             │                   │        + Puppeteer           │
│  • doctors              │                   │                              │
│  • drugs                │◄─────────────────►│  Sends medication reminders  │
│  • drug_slots           │                   │  via WhatsApp messages       │
│  • schedule             │                   └──────────────────────────────┘
│  • uploads              │
└─────────────────────────┘
```

### Agent Flow

1. **User speaks** into the microphone via the web interface
2. **Web Speech API** converts speech to text
3. **Frontend** sends text to backend's `/api/chat` endpoint
4. **Agent Router** analyses intent and routes to the appropriate specialised agent
5. **Specialised Agent** executes tools (database queries, bookings, etc.)
6. **Response** is returned to the frontend and optionally spoken aloud (TTS)
7. **WhatsApp Service** sends medication reminders at scheduled times

## ✨ Features

### 🎤 Voice Interface
- **Voice-controlled interaction** using Web Speech API for speech-to-text
- **Real-time transcription** of user speech
- **Natural language understanding** powered by Google Gemini AI

### 🤖 AI Agents
- **Agent Router**: Intelligently routes requests to specialised agents
- **Scheduling Agent**: Manages appointment scheduling and availability
- **Booking Agent**: Handles appointment confirmations and modifications
- **Notification Agent**: Sends alerts and reminders
- **Medication Reminder Agent**: Manages drug schedules and WhatsApp reminders

### 💊 Prescription Management
- **Prescription upload** (image/PDF support)
- **AI-powered extraction** of doctor info and medications using Gemini AI
- **Automatic drug slot creation** (morning, afternoon, night)
- **Duplicate detection** via file hashing

### 📱 Notifications
- **WhatsApp integration** for medication reminders
- **Real-time tool execution visualisation** in the UI
- **Persistent WhatsApp sessions** across container restarts

### 🔐 Authentication
- **JWT-based authentication** with secure token management
- **bcrypt password hashing** for secure credential storage
- **Protected API endpoints** requiring valid tokens
- **User registration and login** flows

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | React + TypeScript | Modern reactive UI framework |
| **Styling** | TailwindCSS | Utility-first CSS framework |
| **Build Tool** | Vite | Fast development and production builds |
| **Backend** | FastAPI + Python | High-performance async API framework |
| **AI Engine** | Google Gemini 3 Flash | Natural language processing and generation |
| **WhatsApp Bridge** | whatsapp-web.js + Puppeteer | WhatsApp Web automation |
| **Database** | Supabase (PostgreSQL) | Managed PostgreSQL with real-time capabilities |
| **Authentication** | JWT + bcrypt | Secure token-based auth |
| **Web Server** | Nginx | Reverse proxy and static file serving |
| **Containerisation** | Docker + Docker Compose | Multi-service orchestration |

## 📋 Prerequisites

Before setting up VITA-CARE, ensure you have:

- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **Node.js** (v18+) — for manual development setup
- **Python** (3.9+) — for manual development setup
- **Google Gemini API Key** — [Get one here](https://aistudio.google.com/app/apikey)
- **Supabase Project** — [Create one here](https://supabase.com/dashboard)
- **Git** — for cloning the repository

## 📁 Project Structure

<details>
<summary><strong>Click to expand project structure</strong></summary>

```
VITA-CARE/
├── docker-compose.yml          # Multi-service orchestration
├── docker.env.example          # Environment variables template
├── README.md                   # Documentation
│
├── frontend/                   # React + TypeScript SPA
│   ├── Dockerfile              # Multi-stage build for production
│   ├── nginx.conf              # Nginx reverse proxy config
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.ts          # Vite configuration
│   ├── tailwind.config.js      # TailwindCSS configuration
│   ├── index.html              # Entry HTML file
│   └── src/                    # React source code
│
├── backend/                    # FastAPI + Python API
│   ├── Dockerfile              # Python production image
│   ├── main.py                 # FastAPI application entry
│   ├── agent.py                # Main agent logic
│   ├── auth.py                 # JWT authentication
│   ├── models.py               # Pydantic models
│   ├── supabase_client.py      # Supabase connection
│   ├── supabase_schema.sql     # Database schema
│   ├── prescription_service.py # Prescription extraction
│   ├── tools.py                # Agent tools/functions
│   └── agents/                 # Specialised AI agents
│       ├── agent_router.py
│       ├── scheduling_agent.py
│       ├── booking_agent.py
│       ├── notification_agent.py
│       └── medication_reminder_agent.py
│
└── whatsapp/                   # WhatsApp Bridge Service
    ├── Dockerfile              # Node.js + Chromium image
    ├── package.json            # Node.js dependencies
    ├── main.ts                 # WhatsApp client entry
    └── tsconfig.json           # TypeScript configuration
```

</details>

## 🚀 Quick Start with Docker

This is the **recommended** method for running VITA-CARE.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Nithin0306/VITA-CARE.git
cd VITA-CARE
```

### Step 2: Configure Environment Variables

```bash
# Copy the example environment file
cp docker.env.example .env

# Edit .env and fill in your values
nvim .env  # or use your preferred editor
```

Required variables to configure:
- `GEMINI_API_KEY` — Your Google Gemini API key
- `SUPABASE_URL` — Your Supabase project URL
- `SUPABASE_KEY` — Your Supabase anon/public key
- `JWT_SECRET` — A random 32+ character secret (generate with `openssl rand -hex 32`)

### Step 3: Set Up the Database

Run the SQL schema in your Supabase SQL Editor:

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Navigate to **SQL Editor**
3. Copy and paste the contents of `backend/supabase_schema.sql`
4. Click **Run**

### Step 4: Build and Run

```bash
docker compose up --build
```

### Step 5: Access the Application

| Service | URL |
|---------|-----|
| Frontend | [http://localhost](http://localhost) |
| Backend API | [http://localhost:8000](http://localhost:8000) |
| API Docs | [http://localhost:8000/docs](http://localhost:8000/docs) |

### Step 6: Set Up WhatsApp (First Run)

On the first run, you'll need to scan a QR code to link WhatsApp:

```bash
# View WhatsApp service logs
docker compose logs -f whatsapp
```

Scan the QR code displayed in the terminal with your WhatsApp mobile app.

## 🔧 Manual Setup (Development)

For local development without Docker, set up each service individually.

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at [http://localhost:5173](http://localhost:5173).

### WhatsApp Service Setup

```bash
cd whatsapp

# Install dependencies
npm install

# Run the service
npx ts-node main.ts
```

> **Note:** You'll need to scan a QR code on the first run to authenticate WhatsApp.

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key for AI processing |
| `SUPABASE_URL` | ✅ | Your Supabase project URL (e.g., `https://xyz.supabase.co`) |
| `SUPABASE_KEY` | ✅ | Supabase anon/public key for API access |
| `JWT_SECRET` | ✅ | Secret key for JWT token signing (min 32 characters) |
| `JWT_ALGORITHM` | ❌ | JWT algorithm (default: `HS256`) |
| `JWT_EXPIRATION_HOURS` | ❌ | Token expiration time in hours (default: `24`) |

## 📚 API Documentation

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check — returns API status |
| `POST` | `/api/register` | Register a new user account |
| `POST` | `/api/login` | Authenticate and receive JWT token |

### Protected Endpoints

> These endpoints require a valid JWT token in the `Authorization: Bearer <token>` header.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/profile` | Get current user's profile |
| `POST` | `/api/chat` | Main AI agent interaction endpoint |
| `POST` | `/api/upload_prescription` | Upload and process a prescription |

### Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/agents/schedule` | Direct access to Scheduling Agent |
| `POST` | `/agents/book` | Direct access to Booking Agent |
| `POST` | `/agents/notify` | Direct access to Notification Agent |
| `POST` | `/agents/medication` | Direct access to Medication Reminder Agent |

<details>
<summary><strong>View Request/Response Examples</strong></summary>

**Register User**
```bash
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "name": "John Doe",
    "password": "securepassword123",
    "email": "john@example.com",
    "phone": "+1234567890",
    "dob": "1990-01-15"
  }'
```

**Login**
```bash
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

**Chat with Agent**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "message": "Schedule an appointment with Dr. Smith for next Monday",
    "conversation_history": []
  }'
```

</details>

## 🗄️ Database Schema

VITA-CARE uses **6 main tables** in Supabase (PostgreSQL):

| Table | Description |
|-------|-------------|
| `patients` | User accounts with authentication info (username, password hash, contact details) |
| `doctors` | Doctor records extracted from prescriptions |
| `drugs` | Medication records linked to patients and uploads |
| `drug_slots` | Medication timing slots (morning, afternoon, night) |
| `schedule` | Appointment and medication schedule records |
| `uploads` | Audit trail for uploaded prescription files |

### Entity Relationships

```
patients ──┬──< uploads ──< drugs ──< drug_slots
           │
           └──< doctors ──< schedule
```

- **patients** is the central entity (one-to-many with most tables)
- **uploads** tracks prescription files and links to extracted data
- **drugs** and **drug_slots** manage medication schedules
- **schedule** connects patients with doctors for appointments

📍 **Schema Location:** `backend/supabase_schema.sql`

## 📖 Usage Guide

### Interacting with the Voice Assistant

1. **Log in** or **register** on the web interface
2. **Click the microphone button** to activate voice input
3. **Speak your request** clearly (e.g., "Schedule an appointment with Dr. Smith")
4. **View the response** in the chat interface
5. **Monitor tool execution** in the real-time visualisation panel

### Example Conversation Flow

```
User: "I need to schedule an appointment with a cardiologist"
Agent: "I can help you schedule an appointment. When would you like to visit?"

User: "Next Tuesday afternoon"
Agent: "I've found availability on Tuesday at 2:30 PM. Shall I book this slot?"

User: "Yes, please book it"
Agent: "Your appointment has been confirmed for Tuesday at 2:30 PM.
        You'll receive a reminder 24 hours before."
```

### Uploading a Prescription

1. Navigate to the **Prescription Upload** section
2. Click **Upload** and select an image or PDF of your prescription
3. The AI will automatically extract:
   - Doctor name and ID
   - Medication names
   - Dosage schedules (morning/afternoon/night)
4. Review the extracted information
5. Medication reminders will be set up automatically

## 📌 Assumptions

1. **Stable Internet Connection**: Users have reliable internet access for voice recognition, API calls, and WhatsApp integration.

2. **Pre-configured Supabase**: The Supabase project is set up with the provided schema before running the application.

3. **Gemini API Access**: Users have valid access to Google Gemini API with sufficient quota.

4. **WhatsApp QR Authentication**: The WhatsApp service requires an initial manual QR code scan; subsequent sessions are persisted.

5. **Per-User Data Isolation**: All data (prescriptions, schedules, medications) is stored and accessed on a per-user basis.

6. **Browser Compatibility**: Voice recognition requires a modern browser with Web Speech API support (Chrome, Edge recommended).

7. **No Medical Recommendations**: The system does not provide medical advice; all interactions are administrative in nature.

## ⚠️ Known Limitations

1. **WhatsApp Session Management**: The WhatsApp service requires a manual QR code scan on the first run. If the session expires, a new scan is needed.

2. **Browser Voice Support**: Voice recognition depends on browser support. Chrome and Edge provide the best experience; Safari and Firefox have limited support.

3. **Doctor Availability Calendar**: The doctor availability and calendar integration is in development and not fully implemented.

4. **Language Support**: Currently supports English only. Multi-language support is planned for future releases.

5. **Prescription Encryption**: Uploaded prescriptions are stored in Supabase but are not end-to-end encrypted at rest.

6. **API Rate Limits**: Google Gemini API has rate limits that may affect high-volume usage. Consider implementing request queuing for production.

7. **No Offline Mode**: All features require an active internet connection; there is no offline functionality.

## 🔧 Troubleshooting

<details>
<summary><strong>Docker container fails to start</strong></summary>

**Problem:** Backend container shows health check failures.

**Solution:**
1. Check that all environment variables are set in `.env`
2. Verify Supabase URL and key are correct
3. Ensure the database schema is applied
4. View logs: `docker compose logs backend`

</details>

<details>
<summary><strong>WhatsApp QR code not appearing</strong></summary>

**Problem:** WhatsApp service runs but no QR code is displayed.

**Solution:**
1. Check container logs: `docker compose logs whatsapp`
2. Ensure Puppeteer has access to Chromium
3. Try removing the session volume: `docker volume rm vita-care_whatsapp-session`
4. Restart the service: `docker compose restart whatsapp`

</details>

<details>
<summary><strong>Voice recognition not working</strong></summary>

**Problem:** Microphone button doesn't respond or transcription fails.

**Solution:**
1. Use Chrome or Edge browser (best Web Speech API support)
2. Allow microphone permissions when prompted
3. Check browser console for errors
4. Ensure HTTPS or localhost (required for microphone access)

</details>

<details>
<summary><strong>Gemini API errors</strong></summary>

**Problem:** Chat returns errors about API key or quota.

**Solution:**
1. Verify `GEMINI_API_KEY` is set correctly
2. Check API key validity at [Google AI Studio](https://aistudio.google.com/)
3. Review quota limits in Google Cloud Console
4. If testing, the API will return mock responses without a key

</details>

<details>
<summary><strong>Database connection fails</strong></summary>

**Problem:** Backend cannot connect to Supabase.

**Solution:**
1. Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
2. Check that RLS (Row Level Security) is properly configured
3. Ensure the schema has been applied via SQL Editor
4. Test connection: `curl <SUPABASE_URL>/rest/v1/`

</details>