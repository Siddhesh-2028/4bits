import datetime
from typing import List, Optional, Dict, Any
import uuid
from models import Patient, Appointment, InteractionLog

# --- Mock Data ---
PATIENTS_DB = {
    "P001": Patient(id="P001", name="Alice Smith", dob="1985-04-12", phone="555-0101", last_visit="2025-12-15", next_follow_up_due="2026-01-15"),
    "P002": Patient(id="P002", name="Bob Jones", dob="1978-09-23", phone="555-0102", last_visit="2025-11-20"),
}

APPOINTMENTS_DB = [
    Appointment(id="A100", patient_id="P001", datetime="2026-01-20T10:00:00", type="Follow-up", status="Confirmed"),
]

INTERACTION_LOGS = []

# --- Helper Functions ---

def _generate_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

# --- Tool Implementations ---

def get_patient_record(patient_id: str):
    """
    Fetches patient metadata.
    Args:
        patient_id: The ID of the patient.
    """
    patient = PATIENTS_DB.get(patient_id)
    if not patient:
        return {"error": "Patient not found", "status": "failed"}
    return patient.model_dump()

def check_appointment_availability(date_str: str):
    """
    Queries available slots for a given date.
    Args:
        date_str: Date in YYYY-MM-DD format.
    """
    try:
        # Validate date format
        query_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD.", "status": "failed"}

    # Mock logic: Slots available every hour from 9 AM to 5 PM
    # In a real app, we'd check against APPOINTMENTS_DB
    available_slots = []
    for hour in range(9, 17):
        slot_time = f"{query_date}T{hour:02}:00:00"
        # Check collision
        is_taken = any(appt.datetime == slot_time and appt.status != "Cancelled" for appt in APPOINTMENTS_DB)
        if not is_taken:
            available_slots.append(slot_time)
            
    if not available_slots:
        return {"message": "No slots available for this date.", "available_slots": []}
        
    return {"message": "Slots available.", "available_slots": available_slots}

def book_appointment(patient_id: str, datetime_str: str, appointment_type: str = "Follow-up"):
    """
    Creates a new appointment.
    Args:
        patient_id: The ID of the patient.
        datetime_str: The requested date and time in ISO format (YYYY-MM-DDTHH:MM:SS).
        appointment_type: Type of appointment.
    """
    # 1. Validation
    if patient_id not in PATIENTS_DB:
        return {"error": "Invalid patient ID", "status": "failed"}
    
    # Check for existing booking at same time
    is_taken = any(appt.datetime == datetime_str and appt.status != "Cancelled" for appt in APPOINTMENTS_DB)
    if is_taken:
        return {"error": "Slot already taken", "status": "failed"}

    # 2. Book
    new_appt = Appointment(
        id=_generate_id("APT"),
        patient_id=patient_id,
        datetime=datetime_str,
        type=appointment_type,
        status="Confirmed"
    )
    APPOINTMENTS_DB.append(new_appt)
    
    return {"message": "Appointment booked successfully.", "appointment": new_appt.model_dump(), "status": "success"}

def reschedule_appointment(appointment_id: str, new_datetime_str: str):
    """
    Reschedules an existing appointment.
    Args:
        appointment_id: The ID of the appointment to reschedule.
        new_datetime_str: The new date and time in ISO format.
    """
    # Find appointment
    appt = next((a for a in APPOINTMENTS_DB if a.id == appointment_id), None)
    if not appt:
        return {"error": "Appointment not found", "status": "failed"}
    
    if appt.status == "Cancelled":
         return {"error": "Cannot reschedule a cancelled appointment.", "status": "failed"}

    # Check new slot availability
    is_taken = any(a.datetime == new_datetime_str and a.status != "Cancelled" and a.id != appointment_id for a in APPOINTMENTS_DB)
    if is_taken:
        return {"error": "New slot is unavailable.", "status": "failed"}
        
    old_datetime = appt.datetime
    appt.datetime = new_datetime_str
    
    return {
        "message": "Appointment rescheduled successfully.",
        "old_datetime": old_datetime,
        "new_datetime": new_datetime_str,
        "status": "success"
    }

def cancel_appointment(appointment_id: str):
    """
    Cancels an appointment.
    Args:
        appointment_id: The ID of the appointment.
    """
    appt = next((a for a in APPOINTMENTS_DB if a.id == appointment_id), None)
    if not appt:
        return {"error": "Appointment not found", "status": "failed"}
        
    appt.status = "Cancelled"
    return {"message": "Appointment cancelled.", "status": "success"}

def log_interaction(patient_id: Optional[str], action: str, tool_used: str, outcome: str, details: str = ""):
    """
    Logs an interaction for audit purposes.
    Args:
        patient_id: ID of patient involved (optional).
        action: Description of the action.
        tool_used: Name of the tool used.
        outcome: Success/Failure/Escalation.
        details: Additional context.
    """
    log_entry = InteractionLog(
        id=_generate_id("LOG"),
        timestamp=datetime.datetime.now().isoformat(),
        patient_id=patient_id,
        action=action,
        tool_used=tool_used,
        outcome=outcome,
        details=details
    )
    INTERACTION_LOGS.append(log_entry)
    return {"status": "logged"}

# Tool Dictionary for Agent
TOOLS_MAP = {
    "get_patient_record": get_patient_record,
    "check_appointment_availability": check_appointment_availability,
    "book_appointment": book_appointment,
    "reschedule_appointment": reschedule_appointment,
    "cancel_appointment": cancel_appointment,
    "log_interaction": log_interaction
}
