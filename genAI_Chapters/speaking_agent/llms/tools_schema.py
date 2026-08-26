from google.genai import types
from tools.registry import TOOL_MAP

def build_tools()-> list[types.Tool]: 
    declarations = [] 
    for name , tool_info in TOOL_MAP.items : 
        schema = tool_info["schema"].model_json_schema()
        
        declaration = types.FunctionDeclaration(
            name=name,
            description=tool_info["description"],
            
            parameters_json_schema=schema,
        )
        declarations.append(declaration)
    return [
        types.Tool(
            function_declarations=declarations
        )
    ]  
TOOLS = build_tools()      # jo bi TOOLS call karra, unne build_tools hi chalata
