from pydantic import BaseModel
from typing import Optional
import datetime


class BarberoBase(BaseModel):
    nombre: str


class BarberoCreate(BarberoBase):
    pass


class BarberoUpdate(BaseModel):
    nombre: Optional[str] = None
    activo: Optional[bool] = None


class BarberoOut(BarberoBase):
    id_barbero: int
    activo: bool
    foto_url: Optional[str] = None
    created_at: Optional[datetime.datetime]

    tiene_usuario: bool

    class Config:
        from_attributes = True
