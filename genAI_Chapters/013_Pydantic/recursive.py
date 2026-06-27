from typing import List,Optional
from pydantic import BaseModel

class unit(BaseModel):
    id : int
    content : str
    recall : Optional[List['unit']] = None
    
unit.model_rebuild

un = unit(
    id=4,
    content = "content_1",
    recall = unit(
        id=5,
        content = "content_2",
        recall= unit(
            id=6,
            content= "content_3",  
        ) 
        
    )
)    
    
    
    