from pydantic import BaseModel,field_validator,model_validator
class User(BaseModel): 
    id : int
    name : str
    is_on_mission : bool
    # lets say the id 5 is admins id, noone else is entitled to use it
    @field_validator("id")
    @classmethod
    def id_check(cls,id):
        if(id == 5):
            print("Thats my id")
            raise ValueError(f"my id: {id} is not your property")
        return id,
input_dict = {"id": 5, "name":"silva","is_on_mission": True}            
user1 = User(**input_dict)
print(user1)            