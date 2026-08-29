from google.genai import types
from pydantic import ValidationError

from models.schemas import ToolResult, PendingAction
from tools import policy, registry


def execute_tool_call(tool_call) -> ToolResult:
    function_name = tool_call.name # gemini jo tool function demand kara, woh name nikale bahar
    # yahan gemini ke bataye function ku apne tool_map ke dict me search n bring karre
    tool_definition = registry.TOOL_REGISTRY.get(function_name) # toolmap dict se predefined function schema ke predefined properties eg: function,pydantic schema wagera laye

    if tool_definition is None: # agar gemini kuch aisa demand kare jo apne map me hai hi nahi
        return ToolResult(
            success=False,
            error=f"Unknown tool: {function_name}", # shortterm context maintaince for llm taki unne recent activities ke bareme malumat rakhe
        )

    schema = tool_definition.schema # apne tool_map ke ander decided function ke properties ku bahar nikale
    function = tool_definition.function

    try:
        # yahan response schema me tool_call me ek args rehta jo llm fill karke diya apne ku, woh apni query based rehta, 
                # like tool_call.args for weather function would be "hyderabad", if we ask about hyd weather to llm
        arguments = schema.model_validate( #schema ek pydantic rule hai, jispe model validate tool_args qualify hota ya nahi [tool_args llm banake diya] 
            tool_call.args or {} # tool_call.arg nahi chala toh {} do, taki atleast incorrect format error niyana
        )
    except ValidationError as e:
        return ToolResult(
            success=False,
            error=f"Invalid tool arguments: {e}", # shortterm context maintaince for llm taki unne recent activities ke bareme malumat rakhe
        )
    argument_data = arguments.model_dump()

    if policy.requires_confirmation(
        tool_definition,
        argument_data,
    ):
        return ToolResult(
            success=False,
            requires_confirmation=True,
            error=(
                "User confirmation is required "
                "before executing this action."
            ),
            pending_action=PendingAction(
                tool_name=function_name,
                arguments=argument_data,
            ),
        )
        # else direct nikaljara result banane function ki taraf    

    try: # Execute validated tool.
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
def execute_pending_action(
    action: PendingAction,
) -> ToolResult:
    
    tool_info = registry.TOOL_REGISTRY.get(
        action.tool_name
    )

    if tool_info is None:
        return ToolResult(
            success=False,
            error=f"Unknown tool: {action.tool_name}",
        )

    function = tool_info.function

    try:
        return function(
            **action.arguments
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=f"Tool execution failed: {e}",
        )