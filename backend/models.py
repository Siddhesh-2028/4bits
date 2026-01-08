from typing import Any, Dict, List, Optional

from pydantic import BaseModel


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
