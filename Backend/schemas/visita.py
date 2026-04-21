from pydantic import BaseModel, Field, field_validator
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
    medio_pago: Optional[Literal["mercadopago"]] = None
    # Mismo origen que el navegador (ej. http://192.168.x.x:5173); si no, MP usa PUBLIC_FRONTEND_URL y el retorno puede fallar.
    frontend_return_base: Optional[str] = None

    @field_validator("frontend_return_base", mode="before")
    @classmethod
    def _normalize_frontend_return_base(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        s = str(v).strip().rstrip("/")
        if not s.startswith(("http://", "https://")):
            return None
        if len(s) > 512:
            return None
        return s


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

    cliente_nombre: str
    cliente_apellido: str
    cliente_telefono: Optional[str] = None

    servicio_nombre: str
    servicio_duracion: int
    servicio_precio: Optional[float] = None  # para total estimado en Mi Agenda

    barbero_id: Optional[int] = None
    barbero_nombre: str = ""

    medio_pago: Optional[str] = None
    mercadopago_payment_id: Optional[str] = None
    mercadopago_receipt_url: Optional[str] = None
    mercadopago_seller_activity_url: Optional[str] = None
    mercadopago_init_point: Optional[str] = Field(
        None,
        description="URL de Checkout Pro al crear el turno con Mercado Pago.",
    )
    mercadopago_preference_id: Optional[str] = None
    token_seguimiento: Optional[str] = None
    mercadopago_checkout_error: Optional[str] = Field(
        None,
        description="Si no hubo init_point, motivo breve (configuración o error MP).",
    )

    class Config:
        from_attributes = True
