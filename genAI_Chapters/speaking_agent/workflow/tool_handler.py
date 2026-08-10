from pydantic import ValidationError
from google.genai import types

from llms import history as his
from llms import chat
from tools_unit import registry

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
            function_name = tool_call.name # gemini jo tool function demand kara, woh name nikale bahar

            # yahan gemini ke bataye function ku apne tool_map ke dict me search n bring karre
            tool_info = registry.TOOL_MAP.get(function_name) # toolmap dict se predefined function schema ke predefined properties eg: function,pydantic schema wagera laye

            if tool_info is None: # agar gemini kuch aisa demand kare jo apne map me hai hi nahi
                tool_response_parts.append(
                    types.Part.from_function_response(
                        name=function_name,
                        response={
                            "error": f"Unknown tool: {function_name}" # shortterm context maintaince for llm taki unne recent activities ke bareme malumat rakhe
                        },
                    )
                )
                continue

            schema = tool_info["schema"] # apne tool_map ke ander decided function ke properties ku bahar nikale
            function = tool_info["function"]

            # Validate LLM-generated arguments.
            try:
                arguments = schema.model_validate(tool_call.args or {}) # yahan response schema me tool_call me ek args rehta jo llm fill karke diya apne ku, woh apni query based rehta, 
                # like tool_call.args for weather function would be "hyderabad", if we ask about hyd weather to llm
            except ValidationError as e:
                tool_response_parts.append(
                    types.Part.from_function_response(
                        name=function_name,
                        response={
                            "error": (
                                "Invalid tool arguments: " # shortterm context maintaince for llm taki unne recent activities ke bareme malumat rakhe
                                f"{e}"
                            )
                        },
                    )
                )
                continue

            # Execute validated tool.
            try:
                result = function( # yahan [user-query-based]llm decided arg ku json format me function ku dere, function result return karta
                    **arguments.model_dump()
                )
            except Exception as e:
                tool_response_parts.append(
                    types.Part.from_function_response(
                        name=function_name,
                        response={
                            "error": (
                                f"Tool execution failed: {e}"
                            )
                        },
                    )
                )
                continue

            tool_response_parts.append( # append api result in local list, so which can be passed to llm upnext @ line 100
                types.Part.from_function_response(
                    name=function_name,
                    response={
                        "result": str(result)
                    },
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