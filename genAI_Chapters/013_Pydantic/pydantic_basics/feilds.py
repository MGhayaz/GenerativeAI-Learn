from pydantic import Field,BaseModel,EmailStr,ConfigDict
from typing import Optional, Annotated

Name = Annotated[ # this is a form of predeclaration of feild requirment to reduce redundancy
    str, Field(   
        min_length = 3, # minimum length of feild
        max_length = 19,# maximum length of feild 
        description = "Name of employee",
        examples = ["Ghayaz"] 
    )
]
Salary = Annotated[ # this is a form of predeclaration of feild requirment to reduce redundancy
    float, Field(
        ge = 12000, # greater than or equal to
        le = 10000000, # lesser than or equal to
        description = "Employee salary" # describes the feild 
    )
]

class Employees(BaseModel):
    model_config = ConfigDict( # configDict is a typr of dict, meant to design pydantic models or frame these model behaviours
         # whenever user pass an extra input like location in this case which was not demanded, then the 
         # "allow" - accepts it,
         # "forbid" - throws an error, 
         # "ignore" - silently deletes
         extra = "allow",
         frozen=True, # makes feild immutable
         validate_assignment=True, # whenever a feild is reassigned, it make sure the new input must also be valid
         str_strip_whitespace=True # make sure no feild in model has spacing at start and end of feild
     )
    name : Name
    department = "General"
    salary : Salary
    email : EmailStr # check email string is valid or not, check @ is present etc
    
employees_data = {"name" : "lalmani Belbase", "department":"Managment","salary":340000, "email":"lalbel241@gmail.com"}
    
lalmani_belbase = Employees(**employees_data)
print(lalmani_belbase)     