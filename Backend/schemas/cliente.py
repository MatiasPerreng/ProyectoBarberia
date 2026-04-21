from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime


class ClienteBase(BaseModel):
    nombre: str
    apellido: str
    telefono: Optional[str] = None


class ClienteCreate(ClienteBase):
    """Alta desde agenda pública: email obligatorio."""

    email: EmailStr


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None


class ClienteOut(ClienteBase):
    id_cliente: int
    email: Optional[EmailStr] = None
    created_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True
