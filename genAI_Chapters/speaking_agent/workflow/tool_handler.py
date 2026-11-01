import time
from google.genai import types

from llms import history as his
from llms import chat
from tools.executor import execute_tool_call
from models.schemas import ToolExecutionSummary,ToolCallRecord

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
        started = time.perf_counter()
        result = execute_tool_call(tool_call)
        latency_ms = int((time.perf_counter() - started) * 1000)

        if result.requires_confirmation:
            summary.requires_confirmation = True
            summary.pending_action = result.pending_action # tool name to tool name and argument to argument pass
        summary.records.append(
            ToolCallRecord(
                tool_name=tool_call.name,
                arguments=dict(tool_call.args or {}),
                status=(
                    "awaiting_confirmation" if result.requires_confirmation
                    else "success" if result.success
                    else "error"
                ),
            result=(result.result or "")[:2000] or None,
            error=(result.error or "")[:2000] or None,
            latency_ms=latency_ms,
            )
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
