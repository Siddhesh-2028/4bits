"""
Scheduling Agent
Handles natural language schedule parsing and slot suggestion
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from uuid import UUID
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import get_supabase_client


class Slot:
    """Represents an available appointment slot"""
    def __init__(self, datetime_str: str, doctor_name: str, doctor_id: str):
        self.datetime = datetime_str
        self.doctor_name = doctor_name
        self.doctor_id = doctor_id

    def to_dict(self) -> Dict:
        return {
            "datetime": self.datetime,
            "doctor_name": self.doctor_name,
            "doctor_id": self.doctor_id
        }


def parse_time_intent(user_input: str) -> Optional[datetime]:
    """
    Parse natural language time expressions
    Returns approximate datetime for scheduling
    """
    user_input_lower = user_input.lower()
    now = datetime.now()

    # Tomorrow
    if "tomorrow" in user_input_lower:
        return now + timedelta(days=1)

    # Next week
    if "next week" in user_input_lower:
        return now + timedelta(days=7)

    # This week
    if "this week" in user_input_lower:
        return now + timedelta(days=3)

    # Specific day patterns
    days_of_week = {
        "monday": 0, "tuesday": 1, "wednesday": 2,
        "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
    }

    for day_name, day_num in days_of_week.items():
        if day_name in user_input_lower:
            current_day = now.weekday()
            days_ahead = (day_num - current_day) % 7
            if days_ahead == 0:
                days_ahead = 7  # Next occurrence
            return now + timedelta(days=days_ahead)

    # Default: suggest slots starting from tomorrow
    return now + timedelta(days=1)


async def get_patient_doctors(pid: UUID) -> List[Dict]:
    """
    Retrieve all doctors associated with a patient via prescriptions
    """
    supabase = get_supabase_client()

    try:
        # Query doctors table for this patient
        response = supabase.table("doctors").select("did, doctor_name, doctor_id_external").eq("pid", str(pid)).execute()

        if not response.data:
            return []

        return response.data
    except Exception as e:
        print(f"Error fetching patient doctors: {e}")
        return []


async def get_existing_appointments(pid: UUID, start_date: datetime) -> List[str]:
    """
    Get existing appointment times for a patient to avoid conflicts
    Returns list of ISO datetime strings
    """
    supabase = get_supabase_client()

    try:
        # Query schedule table for this patient
        # Note: schedule table doesn't have datetime field in current schema
        # For now, we'll return empty list - this can be extended when
        # appointment_time field is added to schedule table
        response = supabase.table("schedule").select("*").eq("pid", str(pid)).execute()

        # TODO: When appointment_time is added to schema, filter by date
        return []
    except Exception as e:
        print(f"Error fetching existing appointments: {e}")
        return []


def generate_available_slots(
    start_date: datetime,
    doctor_name: str,
    doctor_id: str,
    existing_appointments: List[str],
    num_slots: int = 3
) -> List[Slot]:
    """
    Generate available time slots for a doctor
    Mock implementation - in production, this would query doctor availability table
    """
    slots = []
    current_date = start_date.replace(hour=9, minute=0, second=0, microsecond=0)

    # Generate slots between 9 AM and 5 PM, skip weekends
    slot_count = 0
    days_checked = 0
    max_days = 14  # Check up to 2 weeks ahead

    while slot_count < num_slots and days_checked < max_days:
        # Skip weekends
        if current_date.weekday() not in [5, 6]:  # Not Saturday or Sunday
            for hour in [9, 11, 14, 16]:  # 9AM, 11AM, 2PM, 4PM
                slot_time = current_date.replace(hour=hour)
                slot_iso = slot_time.isoformat()

                # Check if slot is not already booked
                if slot_iso not in existing_appointments:
                    slots.append(Slot(slot_iso, doctor_name, doctor_id))
                    slot_count += 1

                    if slot_count >= num_slots:
                        break

        current_date += timedelta(days=1)
        days_checked += 1

    return slots


async def suggest_slots(user_input: str, pid: UUID) -> List[Dict]:
    """
    Main function: Parse user request and suggest available appointment slots

    Args:
        user_input: Natural language scheduling request
        pid: Patient UUID

    Returns:
        List of available slots (max 3)
    """
    try:
        # 1. Parse time intent from user input
        target_date = parse_time_intent(user_input)
        if not target_date:
            target_date = datetime.now() + timedelta(days=1)

        # 2. Get patient's doctors
        doctors = await get_patient_doctors(pid)

        if not doctors:
            return [{
                "error": "No doctors found. Please upload a prescription first.",
                "slots": []
            }]

        # 3. Get existing appointments to avoid conflicts
        existing_appointments = await get_existing_appointments(pid, target_date)

        # 4. Generate slots for the first doctor (can be extended to all doctors)
        primary_doctor = doctors[0]
        doctor_name = primary_doctor["doctor_name"]
        doctor_id = primary_doctor["did"]

        # 5. Generate available slots
        available_slots = generate_available_slots(
            target_date,
            doctor_name,
            doctor_id,
            existing_appointments,
            num_slots=3
        )

        # 6. Return formatted response
        return [slot.to_dict() for slot in available_slots]

    except Exception as e:
        print(f"Error in suggest_slots: {e}")
        return [{
            "error": f"Failed to suggest slots: {str(e)}",
            "slots": []
        }]


# Test function
async def test_scheduling_agent():
    """Test the scheduling agent"""
    # This would need a valid patient UUID from your database
    test_pid = UUID("00000000-0000-0000-0000-000000000000")
    result = await suggest_slots("I need an appointment next week", test_pid)
    print("Suggested slots:", result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_scheduling_agent())
