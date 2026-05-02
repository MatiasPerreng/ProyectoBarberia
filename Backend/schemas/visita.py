from pydantic import BaseModel, Field
from typing import Optional, Literal
import datetime

# ----------------------------------------------------------------------------------------------------------------------
# VISITA BASE
# ----------------------------------------------------------------------------------------------------------------------

class VisitaBase(BaseModel):
    fecha_hora: datetime.datetime
    id_cliente: int
    id_servicio: int


class VisitaCreate(VisitaBase):
    id_barbero: Optional[int] = None  # null = asignar automáticamente
    medio_pago: Literal["efectivo", "mercadopago"] = "efectivo"


# ----------------------------------------------------------------------------------------------------------------------
# UPDATE (ADMIN / BARBERO)
# ----------------------------------------------------------------------------------------------------------------------

class VisitaUpdate(BaseModel):
    fecha_hora: Optional[datetime.datetime] = None
    id_barbero: Optional[int] = None
    id_servicio: Optional[int] = None
    estado: Optional[Literal["reservado", "cancelado", "completado"]] = None


# ----------------------------------------------------------------------------------------------------------------------
# OUTPUT (AGENDA BARBERO / ADMIN / HISTORIAL)
# ----------------------------------------------------------------------------------------------------------------------

class VisitaOut(BaseModel):

    id_visita: int

    fecha_hora: datetime.datetime
    estado: Optional[str]
    created_at: Optional[datetime.datetime]

    medio_pago: Optional[str] = None
    mp_payment_id: Optional[str] = None
    comprobante_mp_url: Optional[str] = None

    cliente_nombre: str
    cliente_apellido: str
    cliente_telefono: Optional[str] = None

    servicio_nombre: str
    servicio_duracion: int
    servicio_precio: Optional[float] = None  # para total estimado en Mi Agenda

    barbero_id: Optional[int] = None
    barbero_nombre: str = ""

    # Solo se rellenan al crear reserva con Checkout Pro (no persisten en el modelo).
    init_point: Optional[str] = Field(default=None, description="URL de pago MP (solo respuesta POST crear)")
    public_key: Optional[str] = Field(default=None, description="Clave pública MP (solo respuesta POST crear)")

    class Config:
        from_attributes = True
