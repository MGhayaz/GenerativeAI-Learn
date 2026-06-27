from pydantic import BaseModel
class car(BaseModel): # inner model
    engine : str
    seats : int         
        
class vehicle(BaseModel): # outer model
    structure_type : car
    wheels : int

input_data = { # nested fields included
    "structure_type" : {
        "engine" : "diesel NA",
        "seats" : 6,
    },
    "wheels" : 4
    }

ScorpioN = vehicle(**input_data)
print(ScorpioN.model_dump)            