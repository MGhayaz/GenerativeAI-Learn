
from google.genai import types

from llms import history as his
from llms import chat
from tools_unit.executor import execute_tool_call
from models.schemas import PendingCommand, ToolExecutionSummary

# NOTE MOST_COMPLEX_THING IN PROJECT ,READ ALL TO UNDERSTAND
def handle_tool_calls(
    response,
    history,
) -> tuple[list, ToolExecutionSummary]:

    history = his.append_assistant(
        history=history,
        response=response,
    )

    tool_response_parts = []

    summary = ToolExecutionSummary()

    for tool_call in response.function_calls:
        result = execute_tool_call(tool_call)

        if result.requires_confirmation:
            summary.requires_confirmation = True

            if tool_call.name == "execute_command":
                summary.pending_command = PendingCommand(
                    command=tool_call.args["command"]
                )

        tool_response_parts.append(
            build_tool_response_part(
                function_name=tool_call.name,
                result=result,
            )
        )

    history = his.append_tool(
        history=history,
        tool_response_parts=tool_response_parts,
    )
    # no gemini followup here - reducted this scripts responsibility
    return history, summary
def build_tool_response_part(
    function_name: str,
    result,
) -> types.Part:

    response = {
        "success": result.success,
        "result": result.result,
        "error": result.error,
    }

    if result.requires_confirmation:
        response["requires_confirmation"] = True

    return types.Part.from_function_response(
        name=function_name,
        response=response,
    )
