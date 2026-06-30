from pydantic import BaseModel
class car(BaseModel): # inner model
    engine : str
    seats : int         
        
class vehicle(BaseModel): # outer model
    structure_type : car
    wheels : int
    transmission : str

input_data = { # nested fields included
    "structure_type" : {
        "engine" : "diesel NA",
        "seats" : 6,
    },
    "wheels" : 4,
    "transmission" : "AT(TC) 6-SPEED"
    }


ScorpioN = vehicle(**input_data) 
print(ScorpioN.model_dump_json()) # mostly used format, apis , file-handling,databases, caching etc
print(ScorpioN.model_dump()) # python ke dict me dikhane ke liye
print(ScorpioN)           # insaan ke liye kaafi, machine ke liye azaab
