import asyncio
import datetime
from uuid import UUID
from typing import Optional

from supabase_client import get_supabase_client
from agents.scheduling_agent import suggest_slots
from agents.booking_agent import book_slot, cancel_booking

# --- Tool Implementations ---

def get_patient_record(patient_id: str):
    """
    Fetches patient metadata from the database.
    Args:
        patient_id: The ID of the patient (UUID).
    """
    supabase = get_supabase_client()
    try:
        response = supabase.table("patients").select("*").eq("pid", patient_id).execute()
        if not response.data:
            return {"error": "Patient not found", "status": "failed"}
        
        patient = response.data[0]
        # Remove sensitive data
        if "password_hash" in patient:
            del patient["password_hash"]
        return patient
    except Exception as e:
        return {"error": f"Database error: {str(e)}", "status": "failed"}


def check_appointment_availability(user_query: str, patient_id: str):
    """
    Checks for available appointment slots based on user's natural language query.
    Args:
        user_query: The user's request (e.g., "I need to see a doctor next week").
        patient_id: The ID of the patient.
    """
    try:
        # Run async agent function synchronously
        slots = asyncio.run(suggest_slots(user_query, UUID(patient_id)))
        return {"slots": slots, "status": "success"}
    except ValueError:
        return {"error": "Invalid patient ID format.", "status": "failed"}
    except Exception as e:
        error_msg = str(e).lower()
        if "quota" in error_msg or "429" in str(e):
            return {"error": "Service is temporarily busy. Please try again.", "status": "rate_limited"}
        return {"error": "Unable to check availability. Please try again.", "status": "failed"}


def book_appointment(
    patient_id: str, doctor_id: str, datetime_str: str, upload_id: Optional[str] = None
):
    """
    Books an appointment. 
    Args:
        patient_id: The ID of the patient.
        doctor_id: The ID of the doctor (obtained from availability check).
        datetime_str: ISO format datetime string of the slot.
        upload_id: Optional prescription ID.
    """
    try:
        slot_dt = datetime.datetime.fromisoformat(datetime_str)
        result = asyncio.run(book_slot(UUID(patient_id), UUID(doctor_id), slot_dt, upload_id))
        return result
    except ValueError as ve:
        if "UUID" in str(ve) or "badly formed" in str(ve).lower():
            return {"error": "Invalid ID format provided.", "status": "failed"}
        return {"error": "Invalid date/time format.", "status": "failed"}
    except Exception as e:
        error_msg = str(e).lower()
        if "quota" in error_msg or "429" in str(e):
            return {"error": "Service is temporarily busy. Please try again.", "status": "rate_limited"}
        return {"error": "Booking failed. Please try again.", "status": "failed"}


def reschedule_appointment(appointment_id: str, new_datetime_str: str):
    """
    Reschedules an existing appointment.
    """
    return {
        "error": "Rescheduling is not currently supported. Please cancel the existing appointment and book a new one.",
        "status": "failed"
    }


def cancel_appointment_tool(schedule_id: str):
    """
    Cancels an existing appointment.
    Args:
        schedule_id: The ID of the appointment schedule.
    """
    try:
        result = asyncio.run(cancel_booking(UUID(schedule_id)))
        return result
    except Exception as e:
        return {"error": f"Cancellation failed: {str(e)}", "status": "failed"}


def log_interaction(
    patient_id: Optional[str],
    action: str,
    tool_used: str,
    outcome: str,
    details: str = "",
):
    """
    Logs an interaction for audit purposes.
    """
    # In a real system, write this to the 'interaction_logs' table
    # For now, we can print it or use a simple fire-and-forget insert
    print(f"[AUDIT] {action} | Tool: {tool_used} | Outcome: {outcome} | User: {patient_id}")
    return {"status": "logged"}


# Tool Dictionary for Agent
TOOLS_MAP = {
    "get_patient_record": get_patient_record,
    "check_appointment_availability": check_appointment_availability,
    "book_appointment": book_appointment,
    "reschedule_appointment": reschedule_appointment,
    "cancel_appointment": cancel_appointment_tool,
    "log_interaction": log_interaction,
}
