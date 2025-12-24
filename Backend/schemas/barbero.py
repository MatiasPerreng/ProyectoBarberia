from pydantic import BaseModel
from typing import Optional
import datetime


class BarberoBase(BaseModel):
    nombre: str


class BarberoCreate(BarberoBase):
    pass


class BarberoUpdate(BaseModel):
    nombre: Optional[str] = None


class BarberoOut(BarberoBase):
    id_barbero: int
    created_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True
