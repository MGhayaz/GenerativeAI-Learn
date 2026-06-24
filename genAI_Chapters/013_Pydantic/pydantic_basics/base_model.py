from pydantic import BaseModel
class User(BaseModel): 
    id : int
    name : str
    is_on_mission : bool
input_data = {"id": 777, "name":"Bond","is_on_mission": True}
# if we provide "777"[str] at the place of int, pydantic convert it silently
# but raise error when incorrect data is given like "ooo777"
user = User(**input_data) # ** to unpack the content present inside dict in sequence
print(user)    