from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


# ==================== EXISTING MODELS ====================
class Patient(BaseModel):
    id: str
    name: str
    dob: str
    phone: str
    last_visit: str
    next_follow_up_due: Optional[str] = None


class Appointment(BaseModel):
    id: str
    patient_id: str
    datetime: str  # ISO format
    type: str  # "Follow-up", "Consultation", etc.
    status: str  # "Confirmed", "Cancelled", "Completed"


class InteractionLog(BaseModel):
    id: str
    timestamp: str
    patient_id: Optional[str] = None
    action: str
    tool_used: Optional[str] = None
    outcome: str
    details: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []  # Role (user/model) -> Content


class ChatResponse(BaseModel):
    response: str
    audio_base64: Optional[str] = None  # For future TTS
    logs: List[Dict[str, Any]] = []
    should_escalate: bool = False


# ==================== AUTHENTICATION MODELS ====================
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=72)  # Bcrypt limit
    name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=10, max_length=15)  # NOW REQUIRED
    email: Optional[str] = None
    dob: Optional[str] = None  # YYYY-MM-DD format
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username must be alphanumeric or contain underscores')
        return v.lower()
    
    @validator('phone')
    def validate_phone(cls, v):
        # Remove spaces and dashes
        cleaned = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not cleaned.isdigit():
            raise ValueError('Phone number must contain only digits')
        if len(cleaned) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return cleaned


class UserLoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    name: str


class UserProfile(BaseModel):
    pid: str
    username: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[str] = None
    created_at: datetime


# ==================== PRESCRIPTION UPLOAD MODELS ====================
class DrugInfo(BaseModel):
    name: str
    slot: Optional[str] = None  # "morning" | "afternoon" | "night"
    
    @validator('slot')
    def validate_slot(cls, v):
        if v and v not in ['morning', 'afternoon', 'night']:
            raise ValueError('Slot must be morning, afternoon, or night')
        return v


class ExtractedPrescriptionData(BaseModel):
    doctor_name: Optional[str] = None
    doctor_id: Optional[str] = None
    drugs: List[DrugInfo] = []


class PrescriptionUploadResponse(BaseModel):
    success: bool
    message: str
    upload_id: Optional[str] = None
    extracted_data: Optional[ExtractedPrescriptionData] = None
    error_details: Optional[str] = None


class MedicationSlot(BaseModel):
    drug_name: str
    drug_id: str
    doctor_name: Optional[str] = None
    uploaded_at: datetime


class MedicationScheduleResponse(BaseModel):
    morning: List[MedicationSlot] = []
    afternoon: List[MedicationSlot] = []
    night: List[MedicationSlot] = []

