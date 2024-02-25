from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CanalModel(BaseModel):
    id: Optional[int] = None
    nome: str
    numero: int

    

