from pydantic import BaseModel
from typing import Optional, List

class UsuarioSchema(BaseModel):
    name: str
    email: str
    password: str
    status: Optional[bool]
    admin: Optional[bool]

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True

class PedidoSchema(BaseModel):
    user_id: int

    class Config:
        from_attributes = True

class ItemSchema(BaseModel):
    quantity: int
    sabor: str
    tamanho: str
    preco_unitario: float

    class Config:
        from_attributes = True

class ResponseOrderSchema(BaseModel):
    id: int
    status: str
    preco: float
    items: List[ItemSchema]

    class Config:
        from_attributes = True