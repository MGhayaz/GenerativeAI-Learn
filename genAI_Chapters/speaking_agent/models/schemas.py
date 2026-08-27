from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict

class ToolDefinition(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    function: Callable[..., Any] # callable ka kaam hai koi callable chiz jaise function ku validate karna
    schema: type[BaseModel]
    description: str
    requires_confirmation : bool = False
    
class WeatherArgs(BaseModel):
    city : str
class CommandArgs(BaseModel):
    command : str
class PendingAction(BaseModel):
    tool_name: str
    arguments: dict  
    
class ToolResult(BaseModel):
    success: bool
    result: str | None = None
    error: str | None = None
    requires_confirmation: bool = False
    pending_action: PendingAction | None = None   
class ToolExecutionSummary(BaseModel):
    requires_confirmation: bool = False
    pending_action: PendingAction | None = None
#STT    
class SpeechResult(BaseModel):
    success: bool
    text: str | None = None
    error: str | None = None  
#TTS
class TTSResult(BaseModel):
    success: bool
    audio_data: bytes | None = None
    error: str | None = None      
    
    
# # PendingAction(
#     tool_name="execute_command",
#     arguments={
#         "command": "Remove-Item test.txt"
#     }
# )    