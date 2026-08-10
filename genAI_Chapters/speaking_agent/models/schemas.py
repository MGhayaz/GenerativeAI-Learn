from pydantic import BaseModel
class WeatherArgs(BaseModel):
    city : str
class WommandArgs(BaseModel):
    command : str