from pydantic import computed_field,BaseModel

class product(BaseModel):
    prize : int
    quantity : int
    
    @computed_field
    @property
    def total_bill (self) -> float:
        return  (self.prize* self.quantity) 
        
input_data = {"prize": 400, "quantity" : 7}    
pr = product(**input_data)
print(pr.total_bill)
# Because of @property, the computed method can be accessed like a normal attribute (without parentheses).

print(pr.model_dump())
# Because of @computed_field, the computed value is included during serialization (e.g., model_dump()) even though it is not a stored model field.