from command import execute_command
from weather import weather
from models.schemas import weatherArgs,commandArgs
TOOL_MAP = {
    "weather" : {
        "function" : weather,
        "schema" : weatherArgs
        },
    "execute_command" : {
        "function" : execute_command,
        "schema" : commandArgs
    }
}