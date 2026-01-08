"""
Agent Router
Orchestrates agent workflow and provides FastAPI endpoints
"""

from datetime import datetime
from typing import Dict, Optional
from uuid import UUID
import sys
import os

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.scheduling_agent import suggest_slots
from agents.booking_agent import book_slot, cancel_booking
from agents.notification_agent import (
    send_notification,
    send_appointment_reminder,
    send_booking_confirmation
)
from agents.medication_reminder_agent import run_reminder_cycle, clear_daily_reminder_cache


# Create FastAPI router
router = APIRouter(prefix="/api/agents", tags=["agents"])


# ==================== REQUEST/RESPONSE MODELS ====================

class SchedulingRequest(BaseModel):
    user_input: str = Field(..., description="Natural language scheduling request")
    patient_id: str = Field(..., description="Patient UUID")


class BookingRequest(BaseModel):
    patient_id: str = Field(..., description="Patient UUID")
    doctor_id: str = Field(..., description="Doctor UUID")
    appointment_time: str = Field(..., description="ISO datetime string")
    upload_id: Optional[str] = Field(None, description="Optional prescription reference")


class CancelBookingRequest(BaseModel):
    schedule_id: str = Field(..., description="Schedule UUID to cancel")


class NotificationRequest(BaseModel):
    contact: str = Field(..., description="Contact identifier")
    message: str = Field(..., description="Message to send")


# ==================== HELPER FUNCTIONS ====================

def get_current_user_from_header(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract user ID from JWT token
    Reuses logic from main.py
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    # Import here to avoid circular dependency
    from auth import decode_access_token
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing user information")

    return user_id


# ==================== AGENT ENDPOINTS ====================

@router.post("/schedule/suggest")
async def suggest_appointment_slots(
    request: SchedulingRequest,
    user_id: str = Depends(get_current_user_from_header)
):
    """
    Suggest available appointment slots based on natural language input

    Example request:
    ```json
    {
        "user_input": "I need an appointment next week",
        "patient_id": "uuid-here"
    }
    ```
    """
    try:
        # Validate patient_id matches authenticated user
        if request.patient_id != user_id:
            raise HTTPException(status_code=403, detail="Cannot schedule for another patient")

        # Call scheduling agent
        slots = await suggest_slots(request.user_input, UUID(request.patient_id))

        return {
            "success": True,
            "slots": slots,
            "message": f"Found {len(slots)} available slots"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")


@router.post("/booking/create")
async def create_booking(
    request: BookingRequest,
    user_id: str = Depends(get_current_user_from_header)
):
    """
    Book an appointment slot

    Example request:
    ```json
    {
        "patient_id": "uuid-here",
        "doctor_id": "uuid-here",
        "appointment_time": "2026-01-15T10:00:00",
        "upload_id": "optional-uuid"
    }
    ```
    """
    try:
        # Validate patient_id matches authenticated user
        if request.patient_id != user_id:
            raise HTTPException(status_code=403, detail="Cannot book for another patient")

        # Parse appointment time
        appointment_dt = datetime.fromisoformat(request.appointment_time)

        # Call booking agent
        result = await book_slot(
            UUID(request.patient_id),
            UUID(request.doctor_id),
            appointment_dt,
            request.upload_id
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Booking failed"))

        # Send confirmation notification (optional)
        try:
            from supabase_client import get_supabase_client
            supabase = get_supabase_client()

            # Get patient phone and doctor name
            patient = supabase.table("patients").select("phone, name").eq("pid", request.patient_id).execute()
            doctor = supabase.table("doctors").select("doctor_name").eq("did", request.doctor_id).execute()

            if patient.data and doctor.data:
                phone = patient.data[0].get("phone")
                doctor_name = doctor.data[0].get("doctor_name")

                if phone:
                    await send_booking_confirmation(phone, doctor_name, request.appointment_time)
        except Exception as notif_error:
            print(f"Failed to send confirmation notification: {notif_error}")

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Booking failed: {str(e)}")


@router.post("/booking/cancel")
async def cancel_appointment(
    request: CancelBookingRequest,
    user_id: str = Depends(get_current_user_from_header)
):
    """
    Cancel an existing appointment

    Example request:
    ```json
    {
        "schedule_id": "uuid-here"
    }
    ```
    """
    try:
        # Verify the schedule belongs to the authenticated user
        from supabase_client import get_supabase_client
        supabase = get_supabase_client()

        schedule = supabase.table("schedule").select("pid").eq("schedule_id", request.schedule_id).execute()

        if not schedule.data:
            raise HTTPException(status_code=404, detail="Appointment not found")

        if schedule.data[0]["pid"] != user_id:
            raise HTTPException(status_code=403, detail="Cannot cancel another patient's appointment")

        # Call booking agent to cancel
        result = await cancel_booking(UUID(request.schedule_id))

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Cancellation failed"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cancellation failed: {str(e)}")


@router.post("/notification/send")
async def send_custom_notification(
    request: NotificationRequest,
    user_id: str = Depends(get_current_user_from_header)
):
    """
    Send a custom notification (admin/testing only)

    Example request:
    ```json
    {
        "contact": "555-1234",
        "message": "Test notification"
    }
    ```
    """
    try:
        result = await send_notification(request.contact, request.message)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notification failed: {str(e)}")


@router.post("/reminders/run")
async def trigger_reminder_cycle():
    """
    Manually trigger medication reminder cycle
    In production, this would be called by a cron job

    No authentication required for cron jobs
    """
    try:
        result = await run_reminder_cycle()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reminder cycle failed: {str(e)}")


@router.post("/reminders/clear-cache")
async def clear_reminder_cache():
    """
    Clear the daily reminder cache
    Should be called once per day
    """
    try:
        result = await clear_daily_reminder_cache()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")


@router.get("/health")
async def agent_health_check():
    """
    Health check endpoint for agent system
    """
    return {
        "status": "healthy",
        "agents": [
            "scheduling_agent",
            "booking_agent",
            "notification_agent",
            "medication_reminder_agent"
        ],
        "timestamp": datetime.now().isoformat()
    }
