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
class ToolCallRecord(BaseModel): # Represents a record of a tool call made during a turn in the conversation, including details about the tool, arguments, status, result, error, and latency.
    tool_name: str
    arguments: dict
    status: ToolCallStatus
    result: str | None = None
    error: str | None = None
    latency_ms: int
    output_chars: int | None = None   # tool ne actual kitna output diya (cap se pehle)        
    truncated: bool = False           # cap laga ya nahi
class UsageSnapshot(BaseModel): # Represents a snapshot of token usage for a single LLM call, including counts for prompt tokens, output tokens, thoughts tokens, cached tokens, tool use prompt tokens, total tokens, and the source of the usage information (either "api" or "estimated").
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    thoughts_tokens: int | None = None
    cached_tokens: int | None = None
    tool_use_prompt_tokens: int | None = None
    total_tokens: int | None = None
    source: Literal["api", "estimated"] = "api"


class LLMCallRecord(BaseModel): # Represents a record of a single LLM call, including the iteration number, usage snapshot, latency in milliseconds, number of attempts, finish reason, key index, and function call count.
    iteration: int
    usage: UsageSnapshot
    latency_ms: int
    attempts: int = 1
    finish_reason: str | None = None
    key_index: int | None = None
    function_call_count: int = 0


class UsageTotals(BaseModel): # Represents aggregated usage totals across multiple LLM calls, including counts for the number of calls, sum of prompt tokens, sum of output tokens, sum of thoughts tokens, sum of cached tokens, and sum of LLM latency in milliseconds.
    call_count: int = 0
    prompt_tokens_sum: int = 0
    output_tokens_sum: int = 0
    thoughts_tokens_sum: int = 0
    cached_tokens_sum: int = 0
    llm_latency_ms_sum: int = 0    

class TurnRecord(BaseModel): # Represents a record of a single turn in a conversation, including the conversation ID, turn index, user message, list of tool call records, assistant message, status of the turn, model used, list of LLM content dictionaries, and the timestamp when the turn was created.
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
    llm_calls: list[LLMCallRecord] = []
    usage_totals: UsageTotals | None = None
    footprint_tokens: int | None = None
    footprint_source: Literal["api", "estimated"] | None = None
    failure_reason: str | None = None    

    
class ToolDefinition(BaseModel): # Represents the definition of a tool that can be called by the assistant, including the callable function, input/output schemas, description, and whether the tool requires confirmation before execution.
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    function: Callable[..., Any] # callable ka kaam hai koi callable chiz jaise function ku validate karna
    schemas: type[BaseModel]
    description: str
    requires_confirmation : bool = False
    
class WeatherArgs(BaseModel): # Represents the arguments required for a weather tool call, including the city for which the weather information is requested.
    city : str
class CommandArgs(BaseModel): # Represents the arguments required for a command execution tool call, including the command string to be executed.
    command : str
class PendingAction(BaseModel): # Represents a pending action that requires confirmation before execution, including the name of the tool to be called and the arguments for the tool call.
    tool_name: str
    arguments: dict  
    
class ToolResult(BaseModel): # Represents the result of a tool call, including whether the call was successful, the result string (if any), an error message (if any), whether confirmation is required for the action, and any pending action details.
    success: bool
    result: str | None = None
    error: str | None = None
    requires_confirmation: bool = False
    pending_action: PendingAction | None = None   
class ToolExecutionSummary(BaseModel): # Represents a summary of the execution of a tool, including whether the execution was successful, the result string (if any), an error message (if any), whether confirmation is required for the action, any pending action details, and a list of tool call records associated with the execution.
    requires_confirmation: bool = False
    pending_action: PendingAction | None = None
    records: list[ToolCallRecord] = []
#STT    
class SpeechResult(BaseModel): # Represents the result of a speech-to-text operation, including whether the operation was successful, the transcribed text (if any), and an error message (if any).
    success: bool
    text: str | None = None
    error: str | None = None  
#TTS
class TTSResult(BaseModel): # Represents the result of a text-to-speech operation, including whether the operation was successful, the generated audio data (if any), and an error message (if any).
    success: bool
    audio_data: bytes | None = None
    error: str | None = None      
    
    
# # PendingAction(
#     tool_name="execute_command",
#     arguments={
#         "command": "Remove-Item test.txt"
#     }
# )    