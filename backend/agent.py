import os

from google import genai
from google.genai import types
from tools import TOOLS_MAP

# VITA-Care Agent System Prompt
SYSTEM_PROMPT = """
You are VITA-Care, a healthcare coordination AI agent.
Your role is to assist with non-diagnostic healthcare workflows such as appointment booking, follow-ups, and reminders.

You must NEVER:
- Provide medical advice
- Diagnose conditions
- Suggest medications
If asked for medical advice, politely refuse and offer to schedule a consultation.

You must:
- Ask clarifying questions when required information is missing
- Confirm critical actions (booking, cancellation) before calling the tool
- Handle interruptions and corrections gracefully
- Use available tools to complete tasks
- Log every action transparently using `log_interaction` after a significant tool use.

The user context (Patient ID) is usually "P001" (Alice Smith) for this demo unless specified otherwise.
If you need to book, always check availability first.
"""


def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    return genai.Client(api_key=api_key)


def process_interaction(user_input: str, conversation_history: list):
    """
    Process input using google-genai SDK with automatic server-side function calling.
    """
    try:
        client = get_client()

        # Prepare tools list (list of callables)
        tool_functions = list(TOOLS_MAP.values())

        # Configure the chat
        # We start a new chat session for each request in this stateless REST API design,
        # but in a real app you'd persist the `chat` object or history.
        # To support function calling, we pass 'tools' in the config.

        chat = client.chats.create(
            model="gemini-3-flash-preview",
            config=types.GenerateContentConfig(
                tools=tool_functions,
                system_instruction=SYSTEM_PROMPT,
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
        return {
            "response": f"System Error (Agent): {str(e)}",
            "logs": [{"error": str(e)}],
        }
