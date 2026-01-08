# VITA-Care: Voice-Integrated Task-Autonomous Care Coordination Agent

## Overview
VITA-Care is a voice-based AI agent designed to assist with non-diagnostic healthcare workflows, such as appointment booking, rescheduling, and follow-up reminders. It uses a **React + TypeScript** frontend for the voice interface and a **FastAPI + Python** backend for the agent logic, powered by **Google Gemini**.

> **⚠️ Medical Disclaimer**: VITA-Care is a concept prototype for administrative coordination only. It **does not** provide medical advice, diagnosis, or treatment strategies.

## Features
- **Voice Control**: Press-to-talk interface using the Web Speech API.
- **Autonomous Agent**: Understands intent (book, reschedule, cancel) and executes tools.
- **Real-time Tool Logs**: Visualizes the agent's "thought process" and backend tool calls.
- **Safety**: Includes validation for patient IDs and appointment availability.

## Tech Stack
- **Frontend**: React, Vite, TailwindCSS, Axios
- **Backend**: FastAPI, Uvicorn, Pydantic, Google Generative AI (Gemini 1.5 Flash)
- **Database**: In-memory mock database (reset on restart)

## Prerequisites
- Node.js (v18+)
- Python (v3.9+)
- **Google Gemini API Key** (Get one [here](https://aistudio.google.com/))

## Setup Instructions

### 1. Backend Setup
1. Navigate to the `backend` folder.
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your API Key:
   - Create a `.env` file in `backend/`:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```
   - OR set it in your terminal:
     ```bash
     export GEMINI_API_KEY=your_api_key_here # Mac/Linux
     set GEMINI_API_KEY=your_api_key_here    # Windows CMD
     $env:GEMINI_API_KEY="your_api_key_here" # Windows PowerShell
     ```
5. Run the server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   Server will run at `http://localhost:8000`.

### 2. Frontend Setup
1. Open a new terminal and navigate to the `frontend` folder.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open the link shown (usually `http://localhost:5173`).

## Usage Guide
1. **Start Interaction**: Click the microphone icon.
2. **Speak**: "Hi, I'm Alice Smith (P001). Can I book a follow-up for next week?"
3. **Agent Response**: The agent will check availability and confirm.
4. **Tools**: Watch the "System Internals" panel to see `get_patient_record` and `check_appointment_availability` being called.

## Troubleshooting
- **Microphone Error**: Ensure you using a modern browser (Chrome/Edge/Safari) and have allowed microphone permissions.
- **Agent Error**: Check the backend terminal for API key errors.
- **CORS Error**: Ensure backend is running on port 8000.
