from pydantic import BaseModel
from typing import Optional
import datetime


class BarberoBase(BaseModel):
    nombre: str
    email: Optional[str] = None


class BarberoCreate(BarberoBase):
    pass


class BarberoUpdate(BaseModel):
    nombre: Optional[str] = None
    foto_url: Optional[str] = None
    activo: Optional[bool] = None


class BarberoOut(BarberoBase):
    id_barbero: int
    activo: bool
    foto_url: Optional[str] = None
    created_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True
