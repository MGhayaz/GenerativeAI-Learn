from pydantic import computed_field,BaseModel

class product(BaseModel):
    prize : int
    quantity : int
    
    
    @property
    @computed_field
    def total_bill (self) -> float:
        return  (self.prize* self.quantity) 
        
input_data = {"prize": 400, "quantity" : 7}    
pr = product(**input_data)
print(pr.total_bill)    # with property decorator, use can use function return value just like it own feild or property
print(pr.model_dump) # with this, you see the undefined feild : total bill which is an function value has been saved in serialization