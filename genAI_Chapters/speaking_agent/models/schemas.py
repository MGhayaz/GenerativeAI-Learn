from pydantic import BaseModel
class WeatherArgs(BaseModel):
    city : str
class CommandArgs(BaseModel):
    command : str
    
class ToolResult(BaseModel): #tool_handler me ane wale nearest possiblilties handle karne ke ek validatiion ka arrangement taki system arg basis me kaam kare nak flow me
    success: bool
    requires_confirmation: bool = False
    result: str | None = None
    error: str | None = None    
class PendingAction(BaseModel):
    tool_name: str
    arguments: dict  
class ToolExecutionSummary(BaseModel):
    requires_confirmation: bool = False
    pending_command: PendingCommand | None = None    
    
    
    
# # PendingAction(
#     tool_name="execute_command",
#     arguments={
#         "command": "Remove-Item test.txt"
#     }
# )    