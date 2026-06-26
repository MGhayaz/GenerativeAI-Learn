from typing import List, Dict,Optional
from pydantic import BaseModel

class cart(BaseModel):
    user_id: int
    item: List[str]
    quantities : Dict[str, int]   
class Blogpost(BaseModel):
    title : str
    content: str
    image_url : Optional[str] = None     