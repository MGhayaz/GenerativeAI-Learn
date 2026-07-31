from client import types
def types_Tool():
    tools = [
        types.Tool(
            function_declarations=[
                # 1. Weather Tool
                types.FunctionDeclaration(
                    name="weather",
                    description="Get current weather of a city",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "city": types.Schema(
                                type=types.Type.STRING,
                                description="City name"
                            )
                        },
                        required=["city"]
                    )
                ),
                # 2. Execute Command Tool
                types.FunctionDeclaration(
                    name="execute_command",
                    description="Execute a shell command on the local machine and return the output.",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "command": types.Schema(
                                type=types.Type.STRING,
                                description="The shell command to execute."
                            )
                        },
                        required=["command"]
                    )
                )
            ]
        )
    ]
    return tools