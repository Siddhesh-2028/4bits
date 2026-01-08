import os

from google import genai
from google.genai import types
from tools import TOOLS_MAP

# VITA-Care Agent System Prompt
SYSTEM_PROMPT_TEMPLATE = """
You are VITA-Care, a healthcare coordination AI agent.
Your role is to assist with non-diagnostic healthcare workflows such as appointment booking, follow-ups, and reminders.

You must NEVER:
- Provide medical advice
- Diagnose conditions
- Suggest medications
If asked for medical advice, politely refuse and offer to schedule a consultation.

You must:
- PRIORITIZE ACTIONS. If the user wants to book, check availability IMMEDIATELY using `check_appointment_availability`.
- Do NOT ask clarifying questions like "when?" or "what type?" before checking availability.
- Confirm critical actions (booking, cancellation) before calling the tool.
- Handle interruptions and corrections gracefully.

The current User ID is "{user_id}".

IMPORTANT RULES:
1. ALWAYS pass "{user_id}" as the `patient_id` argument when calling tools.
2. When the user asks to "book an appointment" or "schedule a visit", IMMEDIATELY call `check_appointment_availability` with "{user_id}" and a query like "next available".
3. After getting slots, present them to the user and ask which one they want.
4. If the user selects a slot, call `book_appointment` with the slot details.
5. Do NOT call `log_interaction` unless explicitly asked to log something.
"""


def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    return genai.Client(api_key=api_key)


def process_interaction(user_input: str, conversation_history: list, user_id: str):
    """
    Process input using google-genai SDK with automatic server-side function calling.
    """
    try:
        client = get_client()

        # Prepare tools list (list of callables)
        tool_functions = list(TOOLS_MAP.values())

        # Dynamic System Prompt
        system_instruction = SYSTEM_PROMPT_TEMPLATE.format(user_id=user_id)

        # Configure the chat
        # We start a new chat session for each request in this stateless REST API design,
        # but in a real app you'd persist the `chat` object or history.
        # To support function calling, we pass 'tools' in the config.

        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                tools=tool_functions,
                system_instruction=system_instruction,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=False, maximum_remote_calls=5
                ),
            ),
        )

        # Send message
        # The SDK handles the multi-turn tool execution loop automatically (if configured).
        response = chat.send_message(user_input)

        # Extract logs
        # With the new SDK, inspecting intermediate tool calls might require
        # checking the chat history or response parts.
        # The history in `chat` should contain the turns.

        # Extract logs
        tool_logs = []
        try:
            # Inspection of history for tool calls
            # Use getattr to be safe across SDK versions/structures
            history_list = getattr(chat, "history", [])
            for content in history_list:
                parts = getattr(content, "parts", [])
                for part in parts:
                    fn_call = getattr(part, "function_call", None)
                    if fn_call:
                        # Convert args to dict if possible
                        args = fn_call.args
                        if hasattr(args, "items"):
                            args = dict(args.items())

                        tool_logs.append(
                            {"tool": fn_call.name, "args": args, "status": "called"}
                        )
        except Exception as log_err:
            print(f"Warning: Could not extract tool logs: {log_err}")

        # The response text
        final_text = response.text

        return {"response": final_text, "logs": tool_logs}

    except Exception as e:
        error_str = str(e).lower()
        
        # Detect specific API errors and return user-friendly messages
        if "429" in str(e) or "resource_exhausted" in error_str or "quota" in error_str:
            return {
                "response": "I'm currently experiencing high demand. Please try again in a minute or two.",
                "logs": [{"error": "API quota exceeded", "status": "rate_limited"}],
            }
        elif "401" in str(e) or "invalid" in error_str and "key" in error_str:
            return {
                "response": "There's a configuration issue with the AI service. Please contact support.",
                "logs": [{"error": "API key issue", "status": "auth_error"}],
            }
        elif "timeout" in error_str or "unavailable" in error_str:
            return {
                "response": "The AI service is temporarily unavailable. Please try again shortly.",
                "logs": [{"error": "Service unavailable", "status": "timeout"}],
            }
        else:
            # Generic fallback - still don't expose raw error
            print(f"Agent error: {e}")  # Log for debugging
            return {
                "response": "I encountered an issue processing your request. Please try again.",
                "logs": [{"error": "Internal error", "status": "failed"}],
            }
