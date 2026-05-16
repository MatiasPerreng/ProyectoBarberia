"""
Precio bruto para Checkout Pro (Uruguay) — Disponibilidad al instante.

El precio del servicio en BD es neto (lo que debe recibir el barbero).
Mercado Pago descuenta comisión base + IVA sobre la comisión; el cliente
paga un monto mayor para que el neto acreditado coincida con precio_neto.

  Precio final = precio_neto / (1 - tasa_total_efectiva)
  tasa_total_efectiva = 5.99% × 1.22 = 7.3078%
"""
from __future__ import annotations

from typing import NamedTuple

MP_COMISION_BASE = 0.0599
MP_IVA_SOBRE_COMISION = 1.22
MP_TASA_TOTAL_EFECTIVA = MP_COMISION_BASE * MP_IVA_SOBRE_COMISION
MP_DIVISOR_NETO = 1.0 - MP_TASA_TOTAL_EFECTIVA


class PrecioMercadoPago(NamedTuple):
    precio_final: float
    monto_extra: float


def calcular_precio_mercadopago(precio_neto: float) -> PrecioMercadoPago:
    """
    Devuelve el monto a cobrar al cliente y el extra de gestión online.

    Ejemplo: precio_neto=350 → precio_final=377.59, monto_extra=27.59
    """
    neto = float(precio_neto)
    if neto < 0:
        raise ValueError("precio_neto no puede ser negativo")
    if neto == 0:
        return PrecioMercadoPago(precio_final=0.0, monto_extra=0.0)
    final = round(neto / MP_DIVISOR_NETO, 2)
    extra = round(final - neto, 2)
    return PrecioMercadoPago(precio_final=final, monto_extra=extra)


def precio_final_mercadopago(precio_neto: float) -> float:
    """Atajo: solo el monto a cobrar (UYU, 2 decimales)."""
    return calcular_precio_mercadopago(precio_neto).precio_final
