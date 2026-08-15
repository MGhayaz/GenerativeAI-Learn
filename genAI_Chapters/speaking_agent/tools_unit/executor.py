from google.genai import types
from pydantic import ValidationError

from models.schemas import ToolResult
from tools_unit import policy, registry


def execute_tool_call(tool_call) -> ToolResult:
    function_name = tool_call.name

    tool_info = registry.TOOL_MAP.get(function_name)

    if tool_info is None:
        return ToolResult(
            success=False,
            error=f"Unknown tool: {function_name}",
        )

    schema = tool_info["schema"]
    function = tool_info["function"]

    try:
        arguments = schema.model_validate(
            tool_call.args or {}
        )
    except ValidationError as e:
        return ToolResult(
            success=False,
            error=f"Invalid tool arguments: {e}",
        )

    if function_name == "execute_command":
        command = arguments.command

        if policy.requires_confirmation(command):
            return ToolResult(
                success=False,
                requires_confirmation=True,
                error="User confirmation is required before executing this command.",
            )

    try:
        result = function(
            **arguments.model_dump()
        )

    except Exception as e:
        return ToolResult(
            success=False,
            error=f"Tool execution failed: {e}",
        )

    if isinstance(result, ToolResult):
        return result

    return ToolResult(
        success=True,
        result=str(result),
    )