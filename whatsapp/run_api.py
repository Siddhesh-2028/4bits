from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import uvicorn

app = FastAPI()

TS_API_URL = "http://localhost:3001/send-message"

class MessageRequest(BaseModel):
    contact: str
    message: str

def send_whatsapp_message(contact: str, message: str):
    """
    Sends a message to a WhatsApp contact via the TypeScript bridge.
    """
    try:
        response = requests.post(
            TS_API_URL,
            json={"contact": contact, "message": message},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        if not result.get("success", False):
            raise Exception(result.get("error", "Unknown error from TS API"))
        return True, None
    except Exception as e:
        return False, str(e)

@app.post("/send")
async def trigger_message_send_post(request: MessageRequest):
    """
    Endpoint to trigger sending a WhatsApp message via POST JSON.
    """
    success, error_msg = send_whatsapp_message(request.contact, request.message)
    
    if not success:
        raise HTTPException(status_code=500, detail=error_msg)
        
    return {
        "contact": request.contact,
        "message": request.message,
        "success": True
    }

@app.get("/send/{contact}/{message}")
async def trigger_message_send_get(contact: str, message: str):
    """
    Endpoint to trigger sending a WhatsApp message via GET path parameters.
    """
    success, error_msg = send_whatsapp_message(contact, message)
    
    if not success:
        raise HTTPException(status_code=500, detail=error_msg)
        
    return {
        "contact": contact,
        "message": message,
        "success": True
    }

@app.get("/status")
async def get_status():
    return {"status": "online"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)