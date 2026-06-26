from typing import List, Dict,Optional
from pydantic import BaseModel,model_validator

class cart(BaseModel):
    user_id: int
    item: List[str]
    quantities :  Optional[Dict[str, int]] = None
    
    @model_validator(mode = "after")
    def check(self):
        if "weapon" in self.item :
            print("we dont sell this")
            raise ValueError("please visit our Dhanbad - UP Branch")    
        return self    
input_take = {"user_id":1, "item": ["weapon"], "quantities": {"G63-semi automatic": 2}}    
lasli = cart(**input_take)
print(lasli)    