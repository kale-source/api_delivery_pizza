from pydantic import BaseModel
from typing import Optional

class UsuarioSchema(BaseModel):
    name: str
    email: str
    password: str
    status: Optional[bool]
    admin: Optional[bool]

    class Config:
        from_attributes = True
        