from pydantic import BaseModel
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
    
    
    
# # PendingAction(
#     tool_name="execute_command",
#     arguments={
#         "command": "Remove-Item test.txt"
#     }
# )    