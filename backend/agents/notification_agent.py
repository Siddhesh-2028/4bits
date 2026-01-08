"""
Notification Agent
Sends notifications via external API
"""

import httpx
from typing import Dict, Optional
import os


# External notification API configuration
NOTIFICATION_API_BASE = os.getenv("NOTIFICATION_API_URL", "https://api.example.com")


async def send_notification(contact: str, message: str) -> Dict:
    """
    Send notification via external API

    API Endpoint: POST /contact/{contact}/message/{message}

    Args:
        contact: Contact identifier (phone number, email, etc.)
        message: Message to send

    Returns:
        Success/failure dict with API response
    """
    try:
        # Construct API endpoint
        endpoint = f"{NOTIFICATION_API_BASE}/contact/{contact}/message/{message}"

        # Make POST request
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(endpoint)

            if response.status_code == 200:
                return {
                    "success": True,
                    "status": "sent",
                    "message": "Notification sent successfully",
                    "contact": contact,
                    "api_response": response.json() if response.text else {}
                }
            else:
                return {
                    "success": False,
                    "status": "failed",
                    "error": f"API returned status {response.status_code}",
                    "contact": contact
                }

    except httpx.TimeoutException:
        return {
            "success": False,
            "status": "failed",
            "error": "Notification API timeout",
            "contact": contact
        }
    except Exception as e:
        print(f"Error sending notification: {e}")
        return {
            "success": False,
            "status": "failed",
            "error": f"Failed to send notification: {str(e)}",
            "contact": contact
        }


async def send_appointment_reminder(contact: str, doctor_name: str, appointment_time: str) -> Dict:
    """
    Send appointment reminder notification

    Args:
        contact: Contact identifier
        doctor_name: Name of the doctor
        appointment_time: Appointment time (ISO format)

    Returns:
        Success/failure dict
    """
    message = f"Reminder: You have an appointment with Dr. {doctor_name} at {appointment_time}"
    return await send_notification(contact, message)


async def send_medication_reminder(contact: str, drug_name: str, slot: str) -> Dict:
    """
    Send medication reminder notification

    Args:
        contact: Contact identifier
        drug_name: Name of medication
        slot: Time slot (morning/afternoon/night)

    Returns:
        Success/failure dict
    """
    message = f"Reminder: Time to take your medication - {drug_name} ({slot})"
    return await send_notification(contact, message)


async def send_booking_confirmation(contact: str, doctor_name: str, appointment_time: str) -> Dict:
    """
    Send booking confirmation notification

    Args:
        contact: Contact identifier
        doctor_name: Name of the doctor
        appointment_time: Appointment time (ISO format)

    Returns:
        Success/failure dict
    """
    message = f"Appointment confirmed with Dr. {doctor_name} on {appointment_time}"
    return await send_notification(contact, message)


# Test function
async def test_notification_agent():
    """Test the notification agent"""
    result = await send_notification("555-1234", "Test notification message")
    print("Notification result:", result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_notification_agent())
