"""
Booking Agent
Handles transactional appointment booking with database validation
"""

from datetime import datetime
from typing import Dict, Optional
from uuid import UUID
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import get_supabase_client


class BookingConfirmation:
    """Represents a booking confirmation"""
    def __init__(self, schedule_id: str, patient_id: str, doctor_id: str,
                 appointment_time: str, status: str = "confirmed"):
        self.schedule_id = schedule_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_time = appointment_time
        self.status = status

    def to_dict(self) -> Dict:
        return {
            "schedule_id": self.schedule_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "appointment_time": self.appointment_time,
            "status": self.status
        }


async def validate_slot_availability(pid: UUID, did: UUID, slot_datetime: datetime) -> bool:
    """
    Validate that a slot is still available
    Check for conflicts in schedule table

    Args:
        pid: Patient UUID
        did: Doctor UUID
        slot_datetime: Requested appointment time

    Returns:
        True if slot is available, False otherwise
    """
    supabase = get_supabase_client()

    try:
        # Note: Current schema doesn't have appointment_time in schedule table
        # This is a placeholder for when the schema is extended
        # For now, we'll do basic validation

        # Check if doctor exists
        doctor_check = supabase.table("doctors").select("did").eq("did", str(did)).execute()
        if not doctor_check.data:
            return False

        # Check if patient exists
        patient_check = supabase.table("patients").select("pid").eq("pid", str(pid)).execute()
        if not patient_check.data:
            return False

        # TODO: When appointment_time is added to schedule table, check:
        # - No existing appointment for this patient at this time
        # - No existing appointment for this doctor at this time

        return True

    except Exception as e:
        print(f"Error validating slot: {e}")
        return False


async def create_booking_record(pid: UUID, did: UUID, upload_id: Optional[str] = None) -> Optional[str]:
    """
    Create a booking record in the schedule table

    Args:
        pid: Patient UUID
        did: Doctor UUID
        upload_id: Optional upload ID (prescription reference)

    Returns:
        schedule_id if successful, None otherwise
    """
    supabase = get_supabase_client()

    try:
        # Get a valid upload_id if not provided
        if not upload_id:
            # Find the most recent upload for this patient and doctor
            upload_query = supabase.table("uploads").select("upload_id").eq("pid", str(pid)).order("upload_timestamp", desc=True).limit(1).execute()

            if upload_query.data:
                upload_id = upload_query.data[0]["upload_id"]
            else:
                # If no uploads exist, we still need one for FK constraint
                # In production, this should be handled differently
                print("Warning: No upload_id found, booking without prescription reference")
                return None

        # Create schedule record
        booking_data = {
            "pid": str(pid),
            "did": str(did),
            "upload_id": upload_id
        }

        response = supabase.table("schedule").insert(booking_data).execute()

        if response.data:
            return response.data[0]["schedule_id"]

        return None

    except Exception as e:
        print(f"Error creating booking: {e}")
        return None


async def book_slot(pid: UUID, did: UUID, slot: datetime, upload_id: Optional[str] = None) -> Dict:
    """
    Main function: Book an appointment slot

    Args:
        pid: Patient UUID
        did: Doctor UUID
        slot: Appointment datetime
        upload_id: Optional prescription reference

    Returns:
        BookingConfirmation dict or error dict
    """
    try:
        # 1. Validate slot availability
        is_available = await validate_slot_availability(pid, did, slot)

        if not is_available:
            return {
                "success": False,
                "error": "Slot is not available or invalid patient/doctor",
                "status": "failed"
            }

        # 2. Create booking record
        schedule_id = await create_booking_record(pid, did, upload_id)

        if not schedule_id:
            return {
                "success": False,
                "error": "Failed to create booking. Please ensure you have uploaded a prescription.",
                "status": "failed"
            }

        # 3. Create confirmation
        confirmation = BookingConfirmation(
            schedule_id=schedule_id,
            patient_id=str(pid),
            doctor_id=str(did),
            appointment_time=slot.isoformat(),
            status="confirmed"
        )

        return {
            "success": True,
            "booking": confirmation.to_dict(),
            "status": "confirmed",
            "message": "Appointment booked successfully"
        }

    except Exception as e:
        print(f"Error in book_slot: {e}")
        return {
            "success": False,
            "error": f"Booking failed: {str(e)}",
            "status": "failed"
        }


async def cancel_booking(schedule_id: UUID) -> Dict:
    """
    Cancel an existing appointment

    Args:
        schedule_id: Schedule UUID to cancel

    Returns:
        Success/failure dict
    """
    supabase = get_supabase_client()

    try:
        # Delete the schedule record
        response = supabase.table("schedule").delete().eq("schedule_id", str(schedule_id)).execute()

        if response.data:
            return {
                "success": True,
                "message": "Appointment cancelled successfully",
                "status": "cancelled"
            }

        return {
            "success": False,
            "error": "Appointment not found",
            "status": "failed"
        }

    except Exception as e:
        print(f"Error cancelling booking: {e}")
        return {
            "success": False,
            "error": f"Cancellation failed: {str(e)}",
            "status": "failed"
        }


# Test function
async def test_booking_agent():
    """Test the booking agent"""
    test_pid = UUID("00000000-0000-0000-0000-000000000000")
    test_did = UUID("00000000-0000-0000-0000-000000000001")
    test_slot = datetime.now()

    result = await book_slot(test_pid, test_did, test_slot)
    print("Booking result:", result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_booking_agent())
