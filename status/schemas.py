from pydantic import BaseModel
from typing import Optional

class statusSchema(BaseModel):
    content: Optional[str] = None