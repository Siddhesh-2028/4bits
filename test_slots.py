
import asyncio
from uuid import UUID
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.agents.scheduling_agent import suggest_slots

async def test():
    print("Testing suggest_slots...")
    pid = UUID("00000000-0000-0000-0000-000000000000") # Mock PID
    try:
        # User query "next week"
        slots = await suggest_slots("next week", pid)
        print(f"Slots found: {len(slots)}")
        for i, slot in enumerate(slots):
            print(f"Slot {i}: {slot}")
            # Verify datetime format
            dt = slot.get("datetime")
            print(f"  Datetime: '{dt}' (Type: {type(dt)})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
