import os
import uuid
from typing import Optional

import uvicorn
from agent import process_interaction
from auth import create_access_token, hash_password, verify_password
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from models import (
    ChatRequest,
    ChatResponse,
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    UserProfile,
)
from supabase_client import get_supabase_client
from agents.agent_router import router as agent_router

load_dotenv()

app = FastAPI(
    title="VITA-Care API",
    description="Voice-Integrated Task-Autonomous Care Coordination Agent",
)

# CORS Setup
origins = [
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:5173",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include agent router
app.include_router(agent_router)


# ==================== HELPER FUNCTIONS ====================
def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """
    Dependency to extract and validate user from JWT token
    Raises HTTPException if token is invalid or missing
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    from auth import decode_access_token
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing user information")

    return user_id


# ==================== PUBLIC ENDPOINTS ====================
@app.get("/")
def read_root():
    return {"status": "VITA-Care Backend Operational", "version": "2.0.0"}


@app.post("/api/register", response_model=AuthResponse)
async def register(request: UserRegisterRequest):
    """
    Register a new user
    Creates patient record in Supabase and returns JWT token
    """
    supabase = get_supabase_client()

    try:
        # Check if username already exists
        existing_user = supabase.table("patients").select("*").eq("username", request.username).execute()

        if existing_user.data and len(existing_user.data) > 0:
            raise HTTPException(status_code=400, detail="Username already exists")

        # Hash password
        password_hash = hash_password(request.password)

        # Insert into database
        new_user = {
            "username": request.username,
            "name": request.name,
            "password_hash": password_hash,
            "email": request.email if request.email else None,  # Handle empty string
            "phone": request.phone,
            "dob": request.dob or None,
        }

        response = supabase.table("patients").insert(new_user).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create user")

        user_data = response.data[0]
        user_id = str(user_data["pid"])

        # Create JWT token
        token_data = {"sub": user_id, "username": request.username}
        access_token = create_access_token(token_data)

        return AuthResponse(
            access_token=access_token,
            user_id=user_id,
            username=request.username,
            name=request.name,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")  # Log internal error
        # Sanitized user-facing error
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")


@app.post("/api/login", response_model=AuthResponse)
async def login(request: UserLoginRequest):
    """
    Login user
    Validates credentials and returns JWT token
    """
    supabase = get_supabase_client()

    try:
        # Find user by username
        response = supabase.table("patients").select("*").eq("username", request.username.lower()).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        user_data = response.data[0]

        # Verify password
        if not verify_password(request.password, user_data["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        user_id = str(user_data["pid"])

        # Create JWT token
        token_data = {"sub": user_id, "username": user_data["username"]}
        access_token = create_access_token(token_data)

        return AuthResponse(
            access_token=access_token,
            user_id=user_id,
            username=user_data["username"],
            name=user_data["name"],
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")


# ==================== PROTECTED ENDPOINTS ====================
@app.get("/api/profile", response_model=UserProfile)
async def get_profile(user_id: str = Depends(get_current_user)):
    """
    Get current user's profile
    Requires valid JWT token
    """
    supabase = get_supabase_client()

    try:
        response = supabase.table("patients").select("*").eq("pid", user_id).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = response.data[0]

        return UserProfile(
            pid=str(user_data["pid"]),
            username=user_data["username"],
            name=user_data["name"],
            email=user_data.get("email") or "Not provided",
            phone=user_data.get("phone") or "Not provided",
            dob=user_data.get("dob") or "Not provided",
            created_at=user_data["created_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Profile fetch error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, user_id: str = Depends(get_current_user)):
    """
    Main endpoint for voice agent interaction.
    Receives text (from STT) and returns agent text response + tool logs.
    NOW REQUIRES AUTHENTICATION
    """

    # If API key is not set, return mock response for testing WITHOUT crashing
    if not os.environ.get("GEMINI_API_KEY"):
        # MOCK BEHAVIOR for safe demo setup
        return ChatResponse(
            response="[MOCK] I received your message: "
            + request.message
            + ". (Please set GEMINI_API_KEY for real AI)",
            logs=[{"tool": "mock_tool", "status": "skipped", "args": {}}],
        )

    result = process_interaction(request.message, request.conversation_history, user_id)

    return ChatResponse(
        response=result["response"],
        logs=result["logs"],
        should_escalate=False,  # TODO: detect escalation keyword
    )


# ==================== PRESCRIPTION UPLOAD ====================
@app.post("/api/upload_prescription")
async def upload_prescription(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    """
    Upload and process a prescription image/PDF
    Extracts doctor info and medications using Gemini AI
    """
    from prescription_service import (
        validate_upload_file,
        calculate_file_hash,
        extract_prescription_data,
        normalize_extracted_data
    )

    try:
        supabase = get_supabase_client()

        # Validate file
        is_valid, error_msg = await validate_upload_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Calculate file hash
        content = await file.read()
        await file.seek(0)
        file_hash = calculate_file_hash(content)

        # Check for duplicate upload
        existing = supabase.table("uploads").select("upload_id").eq("file_hash", file_hash).eq("pid", user_id).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="This prescription has already been uploaded")

        # Extract data using Gemini
        raw_data = await extract_prescription_data(file)

        # Normalize and validate
        normalized_data = normalize_extracted_data(raw_data)

        # Store in database
        # 1. Create upload record
        upload_data = {
            "pid": user_id,
            "file_hash": file_hash,
            "file_name": file.filename,
            "file_size": len(content),
            "file_type": file.content_type,
            "extraction_status": "success"
        }
        upload_result = supabase.table("uploads").insert(upload_data).execute()
        upload_id = upload_result.data[0]["upload_id"]

        # 2. Create or get doctor record
        doctor_data = {
            "doctor_name": normalized_data["doctor_name"],
            "doctor_id_external": normalized_data.get("doctor_id_external"),
            "pid": user_id,
            "upload_id": upload_id
        }

        # Try to find existing doctor
        existing_doctor = supabase.table("doctors").select("did").eq("doctor_name", doctor_data["doctor_name"]).eq("pid", user_id).execute()

        if existing_doctor.data:
            doctor_id = existing_doctor.data[0]["did"]
        else:
            doctor_result = supabase.table("doctors").insert(doctor_data).execute()
            doctor_id = doctor_result.data[0]["did"]

        # 3. Create drug records and drug_slots
        drug_ids = []
        for drug in normalized_data["drugs"]:
            # Insert drug
            drug_data = {
                "pid": user_id,
                "upload_id": upload_id,
                "drug_name": drug["drug_name"]
            }
            drug_result = supabase.table("drugs").insert(drug_data).execute()
            drug_id = drug_result.data[0]["drug_id"]
            drug_ids.append(drug_id)

            # Insert drug slots
            for slot in drug["slots"]:
                slot_data = {
                    "drug_id": drug_id,
                    "slot": slot
                }
                supabase.table("drug_slots").insert(slot_data).execute()

        # 4. Create schedule record
        schedule_data = {
            "pid": user_id,
            "did": doctor_id,
            "upload_id": upload_id
        }
        supabase.table("schedule").insert(schedule_data).execute()

        return {
            "message": "Prescription uploaded successfully",
            "upload_id": upload_id,
            "doctor_name": normalized_data["doctor_name"],
            "doctor_id": normalized_data.get("doctor_id_external"),
            "medications": normalized_data["drugs"]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Prescription upload error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

