"""
Verification test for scheduling and booking agents
"""
import asyncio
from datetime import datetime, timedelta
from uuid import UUID
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.scheduling_agent import suggest_slots
from agents.booking_agent import book_slot
from supabase_client import get_supabase_client

async def verify_scheduling_system():
    print("🚀 Starting Verification Test...")
    
    # Use a real patient ID from the database for verification
    supabase = get_supabase_client()
    patient_res = supabase.table("patients").select("pid").limit(1).execute()
    
    if not patient_res.data:
        print("❌ Error: No patients found in database. Please register a user first.")
        return
        
    pid = UUID(patient_res.data[0]["pid"])
    print(f"✅ Using Patient ID: {pid}")
    
    # 1. Suggest slots
    print("\n1️⃣ Suggesting slots...")
    slots = await suggest_slots("I need an appointment tomorrow", pid)
    
    if "error" in slots[0]:
        print(f"❌ Error suggesting slots: {slots[0]['error']}")
        return
        
    print(f"✅ Found {len(slots)} slots")
    target_slot = slots[0]
    slot_time = datetime.fromisoformat(target_slot["datetime"])
    did = UUID(target_slot["doctor_id"])
    
    # 2. Book a slot
    print(f"\n2️⃣ Booking slot: {slot_time} with Doctor: {did}")
    booking_res = await book_slot(pid, did, slot_time)
    
    if not booking_res["success"]:
        print(f"❌ Booking failed: {booking_res['error']}")
        return
        
    print(f"✅ Booking successful: {booking_res['booking']['schedule_id']}")
    
    # 3. Suggest slots again (should exclude the booked one)
    print("\n3️⃣ Suggesting slots again (expecting filtering)...")
    updated_slots = await suggest_slots("I need an appointment tomorrow", pid)
    
    is_filtered = all(s["datetime"] != target_slot["datetime"] for s in updated_slots)
    
    if is_filtered:
        print("✅ Success: Booked slot was filtered out.")
    else:
        print("❌ Error: Booked slot was NOT filtered out.")
        
    # 4. Try to book the same slot again (should fail)
    print("\n4️⃣ Attempting duplicate booking...")
    dup_booking = await book_slot(pid, did, slot_time)
    
    if not dup_booking["success"]:
        print(f"✅ Success: Duplicate booking was correctly rejected: {dup_booking['error']}")
    else:
        print("❌ Error: Duplicate booking was accepted!")

if __name__ == "__main__":
    asyncio.run(verify_scheduling_system())
