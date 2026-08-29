from google.genai import types

from tools.registry import TOOL_REGISTRY

def build_gemini_tools() -> list[types.Tool]: # it is made in place of tools_maps in order to cater many tools_function schemas 
    declarations = []

    for tool_name, tool_definition in TOOL_REGISTRY.items(): # gemini response tools schema jabtak unne name,tools.info bhar ke diya -means usku jabtak tools ku chalana hai, loop chalta
        schema = tool_definition.schema.model_json_schema()  # schema me pydantic schema dalre in json schema format, ye pydantic schema response banane se pehele, apan ich specify kare in [registry],[schemas] me, in TOOLS_MAP dict

        declarations.append(
            types.FunctionDeclaration(
                name=tool_name,
                description=tool_definition.description,
                parameters=schema,
            )
        )

    return [
        types.Tool(
            function_declarations=declarations
        )
    ]