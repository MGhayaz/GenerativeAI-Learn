from collections.abc import Callable
from typing import Any,Literal
from pydantic import BaseModel, ConfigDict,Field
from datetime import datetime,timezone
ToolCallStatus = Literal[
    "success", "error", "awaiting_confirmation"
]
TurnStatus = Literal[
    "success", "partial_failure", "failed", "awaiting_confirmation"
]
class ToolCallRecord(BaseModel):
    tool_name: str
    arguments: dict
    status: ToolCallStatus
    result: str | None = None
    error: str | None = None
    latency_ms: int

class TurnRecord(BaseModel):
    conversation_id: str
    turn_index: int
    user_message: str
    tool_calls: list[ToolCallRecord] = []
    assistant_message: str | None = None
    status: TurnStatus
    model: str
    llm_contents: list[dict] = []
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
class ToolDefinition(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    function: Callable[..., Any] # callable ka kaam hai koi callable chiz jaise function ku validate karna
    schemas: type[BaseModel]
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
    records: list[ToolCallRecord] = []
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