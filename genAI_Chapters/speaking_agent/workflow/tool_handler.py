
from google.genai import types

from llms import history as his
from llms import chat
from tools_unit.executor import execute_tool_call

from models.schemas import ToolResult

# isku function ke bahr banaye taki inku future me config ke handle kar pana asan aur yaad rahe
MAX_TOOL_CALLS = 5

# NOTE MOST_COMPLEX_THING IN PROJECT ,READ ALL TO UNDERSTAND
def function_handler(response, history):
    tool_call_count = 0

    while response.function_calls:
        tool_call_count += 1

        if tool_call_count > MAX_TOOL_CALLS:
            # instead of making exception, bas error aaye toh raise karare, taki abhi system silently kill nahi dena
            raise RuntimeError(
                f"Maximum tool-call limit of {MAX_TOOL_CALLS} exceeded."
            )

        # Store Gemini's function call response in conversation history. just like it follows the giant loop workflow
        history = his.append_assistant(
            history=history,
            response=response,
        )
        # tools functions/apis se aaye result ku store and supply karne ek simple list banaye
        tool_response_parts = []

        for tool_call in response.function_calls: # jabtak llm generated response schema me function call hai, it can be 1 or 2 or 3 or any, jab tak loop chalao
            result = execute_tool_call(tool_call=tool_call )

            tool_response_parts.append(
                build_tool_response_part(
                    function_name=tool_call.name,
                    result=result,
                )
            )
        # Give all tool results back to Gemini.
        history = his.append_tool(
            history=history,
            tool_response_parts=tool_response_parts,
        )
        # Ask Gemini what to do next.
        response = chat.generate_followup(
            history=history
        )

    return response.text or "" # return llm made response which do have had the function values
def build_tool_response_part(
    function_name: str,
    result: ToolResult,
) -> types.Part:

    if result.success: # see tools_unit scripts or @weather.py line 14 and 20, a tool_result [dict] is return
        response = {
            "success": True,
            "result": result.result,
        }
    else:
        response = {
            "success": False,
            "error": result.error,
        }

        if result.requires_confirmation:
            response["requires_confirmation"] = True

    return types.Part.from_function_response(
        name=function_name,
        response=response,
    )