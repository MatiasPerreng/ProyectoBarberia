import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class MercadoPagoSyncIn(BaseModel):
    """Sincronizar estado del pago tras Checkout Pro o webhook."""

    payment_id: Optional[str] = Field(
        None,
        max_length=64,
        description="ID del pago en MP (query o webhook). Opcional si mandás external_reference.",
    )
    external_reference: Optional[str] = Field(
        None,
        max_length=32,
        description="external_reference (= id_visita) en la preferencia.",
    )
    preference_id: Optional[str] = Field(
        None,
        max_length=64,
        description="ID de preferencia en la URL de retorno.",
    )

    @field_validator("payment_id", "external_reference", "preference_id", mode="before")
    @classmethod
    def vacio_a_none(cls, v):
        if v is None:
            return None
        s = str(v).strip()
        return s if s else None

    @model_validator(mode="after")
    def al_menos_un_identificador(self):
        if not self.payment_id and not self.external_reference and not self.preference_id:
            raise ValueError("Enviá payment_id, external_reference o preference_id.")
        return self


class MercadoPagoAsociarLinkIn(BaseModel):
    """Asociar un pago hecho por link de cobro (sin external_reference) al turno del token."""

    token_seguimiento: str = Field(..., min_length=8, max_length=48)
    payment_id: str = Field(
        ...,
        min_length=1,
        max_length=80,
        description="N° de operación / payment_id (solo dígitos o texto con el número).",
    )


class MercadoPagoReagendarIn(BaseModel):
    """Confirmar un nuevo horario reutilizando un pago tardío ya aprobado."""

    token: str = Field(..., min_length=24, max_length=256)
    fecha_hora: datetime.datetime
    id_barbero: Optional[int] = None
