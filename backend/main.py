from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv

from models import ChatRequest, ChatResponse
from agent import process_interaction

load_dotenv()

app = FastAPI(
    title="VITA-Care API",
    description="Voice-Integrated Task-Autonomous Care Coordination Agent",
)

# CORS Setup
origins = [
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:5173",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "VITA-Care Backend Operational"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main endpoint for voice agent interaction.
    Receives text (from STT) and returns agent text response + tool logs.
    """

    # If API key is not set, return mock response for testing WITHOUT crashing
    if not os.environ.get("GEMINI_API_KEY"):
        # MOCK BEHAVIOR for safe demo setup
        return ChatResponse(
            response="[MOCK] I received your message: "
            + request.message
            + ". (Please set GEMINI_API_KEY for real AI)",
            logs=[{"tool": "mock_tool", "status": "skipped", "args": {}}],
        )

    result = process_interaction(request.message, request.conversation_history)

    return ChatResponse(
        response=result["response"],
        logs=result["logs"],
        should_escalate=False,  # TODO: detect escalation keyword
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
