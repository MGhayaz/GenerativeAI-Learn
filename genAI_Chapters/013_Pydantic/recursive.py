from typing import List, Optional
from pydantic import BaseModel

class unit(BaseModel):
    id: int
    content: str

    # Forward reference: 'unit' is written as a string because the class
    # is referring to itself before its definition is fully complete.
    recall: Optional[List['unit']] = None


# Resolves all forward references (like 'unit') after the class is created.
# This allows Pydantic to correctly understand self-referencing or recursive models.
unit.model_rebuild()


un = unit(
    id=4,
    content="content_1",
    recall=[
        unit(
            id=5,
            content="content_2",
            recall=[
                unit(
                    id=6,
                    content="content_3",
                )
            ],
        )
    ],
)