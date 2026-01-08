# VITA-Care

Autonomous Healthcare Coordination Agent.

## Quick Start (Docker)

Ensure you have Docker and Docker Compose installed, then run:

```bash
docker-compose up --build
```

The services will be available at:
- **Web Interface**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **WhatsApp Bridge**: http://localhost:5000

## Setup

You need to configure the environment variables for the system to function correctly.

### Backend (`backend/.env`)
- `GEMINI_API_KEY`: Your Google Gemini API key.
- `SUPABASE_URL`: Your Supabase project URL.
- `SUPABASE_KEY`: Your Supabase API key.

### WhatsApp (`whatsapp/.env`)
- `PHONE_NUMBER_SERIALIZED`: Your 10-digit phone number.

## WhatsApp Session Persistence
Scan the QR code once. The session is saved in `whatsapp/whatsapp_cache`, so you won't need to re-scan on restarts.

## Medical Disclaimer
VITA-Care is a prototype for administrative coordination only. It does not provide medical advice, diagnosis, or treatment.
