"""
Medication Reminder Agent
Cron-based medication reminder system
"""

from datetime import datetime, time
from typing import List, Dict, Set
from uuid import UUID
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import get_supabase_client
from agents.notification_agent import send_medication_reminder


# Track sent reminders to avoid duplicates (in-memory for now)
# In production, this should be persisted in database
SENT_REMINDERS: Set[str] = set()


def get_current_slot() -> str:
    """
    Determine current medication slot based on time of day

    Returns:
        'morning', 'afternoon', or 'night'
    """
    current_hour = datetime.now().hour

    if 6 <= current_hour < 12:
        return "morning"
    elif 12 <= current_hour < 18:
        return "afternoon"
    else:
        return "night"


async def get_due_medications(slot: str) -> List[Dict]:
    """
    Query database for medications due in the current slot

    Args:
        slot: Time slot (morning/afternoon/night)

    Returns:
        List of medication records with patient contact info
    """
    supabase = get_supabase_client()

    try:
        # Query drug_slots table for the current slot
        # Join with drugs, patients to get complete information
        response = supabase.table("drug_slots").select(
            "slot_id, slot, drug_id, drugs(drug_name, pid, patients(phone, name))"
        ).eq("slot", slot).execute()

        if not response.data:
            return []

        medications = []
        for record in response.data:
            # Extract nested data
            drug_info = record.get("drugs", {})
            patient_info = drug_info.get("patients", {})

            medications.append({
                "slot_id": record["slot_id"],
                "drug_id": record["drug_id"],
                "drug_name": drug_info.get("drug_name", "Unknown"),
                "patient_id": drug_info.get("pid"),
                "patient_name": patient_info.get("name", "Unknown"),
                "patient_phone": patient_info.get("phone", ""),
                "slot": record["slot"]
            })

        return medications

    except Exception as e:
        print(f"Error fetching due medications: {e}")
        return []


def generate_reminder_key(patient_id: str, drug_id: str, slot: str, date: str) -> str:
    """
    Generate unique key for tracking sent reminders

    Args:
        patient_id: Patient UUID
        drug_id: Drug UUID
        slot: Time slot
        date: Date in YYYY-MM-DD format

    Returns:
        Unique reminder key
    """
    return f"{patient_id}:{drug_id}:{slot}:{date}"


async def send_reminders_for_medications(medications: List[Dict]) -> Dict:
    """
    Send reminders for a list of medications

    Args:
        medications: List of medication records

    Returns:
        Summary of sent reminders
    """
    sent_count = 0
    failed_count = 0
    skipped_count = 0
    current_date = datetime.now().strftime("%Y-%m-%d")

    for med in medications:
        # Generate reminder key
        reminder_key = generate_reminder_key(
            med["patient_id"],
            med["drug_id"],
            med["slot"],
            current_date
        )

        # Check if already sent today
        if reminder_key in SENT_REMINDERS:
            skipped_count += 1
            continue

        # Send notification
        contact = med["patient_phone"]
        if not contact:
            print(f"No phone number for patient {med['patient_name']}")
            failed_count += 1
            continue

        result = await send_medication_reminder(
            contact=contact,
            drug_name=med["drug_name"],
            slot=med["slot"]
        )

        if result.get("success"):
            sent_count += 1
            SENT_REMINDERS.add(reminder_key)
        else:
            failed_count += 1
            print(f"Failed to send reminder: {result.get('error')}")

    return {
        "sent": sent_count,
        "failed": failed_count,
        "skipped": skipped_count,
        "total": len(medications)
    }


async def run_reminder_cycle() -> Dict:
    """
    Main function: Run one cycle of medication reminders
    Should be called by cron job at appropriate intervals

    Returns:
        Summary of reminder cycle execution
    """
    try:
        # 1. Determine current slot
        current_slot = get_current_slot()

        # 2. Get medications due for this slot
        due_medications = await get_due_medications(current_slot)

        if not due_medications:
            return {
                "success": True,
                "slot": current_slot,
                "message": "No medications due for this slot",
                "sent": 0,
                "failed": 0,
                "skipped": 0
            }

        # 3. Send reminders
        result = await send_reminders_for_medications(due_medications)

        return {
            "success": True,
            "slot": current_slot,
            "message": f"Reminder cycle completed for {current_slot} slot",
            **result
        }

    except Exception as e:
        print(f"Error in reminder cycle: {e}")
        return {
            "success": False,
            "error": f"Reminder cycle failed: {str(e)}",
            "sent": 0,
            "failed": 0,
            "skipped": 0
        }


async def clear_daily_reminder_cache():
    """
    Clear the reminder cache (should be run once daily)
    In production, this would clean up database records
    """
    global SENT_REMINDERS
    SENT_REMINDERS.clear()
    return {"success": True, "message": "Reminder cache cleared"}


# Test function
async def test_reminder_agent():
    """Test the medication reminder agent"""
    result = await run_reminder_cycle()
    print("Reminder cycle result:", result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_reminder_agent())
