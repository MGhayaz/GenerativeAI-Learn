from command import execute_command
from weather import weather
from models.schemas import WeatherArgs,CommandArgs
TOOL_MAP = {
    "weather" : {
        "function" : weather,
        "schema" : WeatherArgs,
        "description": "Get current weather of a city.",
        },
    "execute_command" : {
        "function" : execute_command,
        "schema" : CommandArgs,
        "description": "Execute a shell command on the local Windows machine and return the output.",
    }
}