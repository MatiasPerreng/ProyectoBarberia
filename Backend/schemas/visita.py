from pydantic import BaseModel
from typing import Optional, Literal
import datetime

# ----------------------------------------------------------------------------------------------------------------------
# VISITA BASE
# ----------------------------------------------------------------------------------------------------------------------

class VisitaBase(BaseModel):
    fecha_hora: datetime.datetime
    id_cliente: int
    id_barbero: int
    id_servicio: int


class VisitaCreate(VisitaBase):
    pass


# ----------------------------------------------------------------------------------------------------------------------
# UPDATE (ADMIN / BARBERO)
# ----------------------------------------------------------------------------------------------------------------------

class VisitaUpdate(BaseModel):
    fecha_hora: Optional[datetime.datetime] = None
    id_barbero: Optional[int] = None
    id_servicio: Optional[int] = None
    estado: Optional[Literal["reservado", "cancelado", "completado"]] = None


# ----------------------------------------------------------------------------------------------------------------------
# OUTPUT (AGENDA BARBERO / ADMIN)
# ----------------------------------------------------------------------------------------------------------------------

class VisitaOut(BaseModel):
    # IDs
    id_visita: int

    # Turno
    fecha_hora: datetime.datetime
    estado: Optional[str]
    created_at: Optional[datetime.datetime]

    # ---------------------------
    # CLIENTE (LO QUE TE FALTABA)
    # ---------------------------
    cliente_nombre: str
    cliente_apellido: str
    cliente_telefono: Optional[str] = None

    # ---------------------------
    # SERVICIO
    # ---------------------------
    servicio_nombre: str
    servicio_duracion: int

    class Config:
        from_attributes = True
