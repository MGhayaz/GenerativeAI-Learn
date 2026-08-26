from command import execute_command
from weather import weather
from models.schemas import WeatherArgs,CommandArgs,ToolDefinition
TOOL_MAP : dict[str,ToolDefinition] = {
    "weather" : ToolDefinition(
        function = weather,
        schema = WeatherArgs,
        description= "Get current weather of a city.",
        requires_confirmation= False,
    ),
    "execute_command" : ToolDefinition(
        function = execute_command,
        schema = CommandArgs,
        description= "Execute a shell command on the local Windows machine and return the output.",
        requires_confirmation= True, # this tool does require confimration from user to make wild changes eg : file deletion etc
    ),
}