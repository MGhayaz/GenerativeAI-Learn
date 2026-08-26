from google.genai import types
from tools.registry import TOOL_MAP

def build_tools()-> list[types.Tool]: # it is made in place of tools_maps in order to cater many tools_function schemas 
    declarations = [] 
    for name , tool_info in TOOL_MAP.items : # gemini response tools schema jabtak unne name,tools.info bhar ke diya -means usku jabtak tools ku chalana hai, loop chalta
        schema = tool_info["schema"].model_json_schema() # schema me pydantic schema dalre in json schema format, ye pydantic schema response banane se pehele, apan ich specify kare in [registry],[schemas] me, in TOOLS_MAP dict
        
        declaration = types.FunctionDeclaration(
            name=name,
            description=tool_info["description"],
            # Google's SDK explicitly supports passing JSON-schema-style parameters through parameters_json_schema
            parameters_json_schema=schema,
        )
        declarations.append(declaration)
    return [
        types.Tool(
            function_declarations=declarations
        )
    ]  
TOOLS = build_tools()      # jo bi TOOLS call karra, unne build_tools hi chalata
