from pydantic import BaseModel
class weatherArgs(BaseModel):
    city : str
class commandArgs(BaseModel):
    command : str