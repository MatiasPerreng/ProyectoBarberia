from pydantic import BaseModel
from typing import Optional
import datetime

# ----------------------------------------------------------------------------------------------------------------------
# HORARIO BASE (CON VIGENCIA)
# ----------------------------------------------------------------------------------------------------------------------

class HorarioBarberoBase(BaseModel):
    dia_semana: int                 # 1 = lunes ... 7 = domingo
    hora_desde: datetime.time
    hora_hasta: datetime.time
    fecha_desde: datetime.date
    fecha_hasta: datetime.date


class HorarioBarberoCreate(HorarioBarberoBase):
    id_barbero: int


class HorarioBarberoUpdate(BaseModel):
    dia_semana: Optional[int] = None
    hora_desde: Optional[datetime.time] = None
    hora_hasta: Optional[datetime.time] = None
    fecha_desde: Optional[datetime.date] = None
    fecha_hasta: Optional[datetime.date] = None


class HorarioBarberoOut(HorarioBarberoBase):
    id_horario: int
    id_barbero: int

    class Config:
        from_attributes = True


# ----------------------------------------------------------------------------------------------------------------------
# EXCEPCIONES DE HORARIO (FUTURO: feriados, cierres, horarios especiales)
# ----------------------------------------------------------------------------------------------------------------------

class HorarioExcepcionBase(BaseModel):
    fecha: datetime.date
    tipo: str  # 'cierre' | 'horario_especial'
    hora_desde: Optional[datetime.time] = None
    hora_hasta: Optional[datetime.time] = None


class HorarioExcepcionCreate(HorarioExcepcionBase):
    id_barbero: int


class HorarioExcepcionOut(HorarioExcepcionBase):
    id_excepcion: int
    id_barbero: int

    class Config:
        from_attributes = True
