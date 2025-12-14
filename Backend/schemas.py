from pydantic import BaseModel
from typing import Optional, List
import datetime
import decimal


class ClienteBase(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    email: Optional[str] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None


class ClienteOut(ClienteBase):
    id_cliente: int
    created_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True

 #----------------------------------------------------------------------------------------------------------------------


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

 #----------------------------------------------------------------------------------------------------------------------

class HorarioBarberoBase(BaseModel):
    dia_semana: int  # 1=Lunes ... 7=Domingo
    hora_desde: datetime.time
    hora_hasta: datetime.time


class HorarioBarberoCreate(HorarioBarberoBase):
    id_barbero: int


class HorarioBarberoOut(HorarioBarberoBase):
    id_horario: int
    id_barbero: int

    class Config:
        from_attributes = True

 #----------------------------------------------------------------------------------------------------------------------

class ServicioBase(BaseModel):
    nombre: str
    duracion_min: int
    precio: decimal.Decimal
    activo: Optional[bool] = True


class ServicioCreate(ServicioBase):
    pass


class ServicioUpdate(BaseModel):
    nombre: Optional[str] = None
    duracion_min: Optional[int] = None
    precio: Optional[decimal.Decimal] = None
    activo: Optional[bool] = None


class ServicioOut(ServicioBase):
    id_servicio: int

    class Config:
        from_attributes = True

 #----------------------------------------------------------------------------------------------------------------------

class VisitaBase(BaseModel):
    fecha_hora: datetime.datetime
    id_cliente: int
    id_barbero: int
    id_servicio: int


class VisitaCreate(VisitaBase):
    pass


class VisitaUpdate(BaseModel):
    fecha_hora: Optional[datetime.datetime] = None
    id_barbero: Optional[int] = None
    id_servicio: Optional[int] = None
    estado: Optional[str] = None  # reservado | cancelado | completado


class VisitaOut(BaseModel):
    id_visita: int
    fecha_hora: datetime.datetime
    estado: str
    created_at: Optional[datetime.datetime]

    cliente: ClienteOut
    barbero: BarberoOut
    servicio: ServicioOut

    class Config:
        from_attributes = True
 #----------------------------------------------------------------------------------------------------------------------